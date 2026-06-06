import argparse
from datetime import datetime
from pathlib import Path
import sys
import time

import cv2

try:
    import tkinter as tk
    from tkinter import messagebox
    from PIL import Image, ImageTk
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "缺少 GUI 依赖。请先安装: pip install pillow\n"
        f"原始错误: {e}"
    )


def _safe_imwrite(path: Path, frame_bgr) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ext = (path.suffix or ".jpg").lower()
    ok, buf = cv2.imencode(ext, frame_bgr)
    if not ok:
        raise ValueError(f"编码失败，无法保存: {path}")
    with open(path, "wb") as f:
        f.write(buf.tobytes())


class CameraApp:
    def __init__(
        self,
        camera_id: int,
        out_dir: Path,
        width: int | None,
        height: int | None,
        fps: int | None,
        fourcc: str | None,
        backend: str,
        window_title: str,
    ):
        self.camera_id = camera_id
        self.out_dir = out_dir
        self.width = width
        self.height = height
        self.fps = fps
        self.fourcc = fourcc
        self.backend = backend
        self.window_title = window_title

        self.root = tk.Tk()
        self.root.title(self.window_title)

        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(fill="both", expand=True)

        btn_row = tk.Frame(self.root)
        btn_row.pack(fill="x", padx=10, pady=10)

        self.btn_capture = tk.Button(btn_row, text="拍照", command=self.capture, height=2, width=12)
        self.btn_capture.pack(side="left")

        self.btn_quit = tk.Button(btn_row, text="退出", command=self.close, height=2, width=12)
        self.btn_quit.pack(side="right")

        self.status_var = tk.StringVar(value=f"Camera: {self.camera_id}")
        self.status = tk.Label(self.root, textvariable=self.status_var, anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0, 10))

        backend_map = {
            "any": cv2.CAP_ANY,
            "dshow": cv2.CAP_DSHOW,
            "msmf": cv2.CAP_MSMF,
        }
        api = backend_map.get(self.backend.lower())
        if api is None:
            raise ValueError("backend 只能是: any / dshow / msmf")

        self.cap = cv2.VideoCapture(self.camera_id, api)
        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError(f"无法打开摄像头 (ID: {self.camera_id})")

        # 注意：很多“4K 摄像头”必须切到 MJPG/H264 才能输出 2160p
        # 设置顺序对部分驱动很关键：FOURCC -> WxH -> FPS -> FOURCC(再设置一次)
        if self.fourcc:
            code = cv2.VideoWriter_fourcc(*self.fourcc.upper())
            self.cap.set(cv2.CAP_PROP_FOURCC, float(code))

        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(self.width))
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self.height))
        if self.fps:
            self.cap.set(cv2.CAP_PROP_FPS, float(self.fps))

        if self.fourcc:
            code = cv2.VideoWriter_fourcc(*self.fourcc.upper())
            self.cap.set(cv2.CAP_PROP_FOURCC, float(code))

        self.last_frame_bgr = None
        self._photo_ref = None
        self._tick_count = 0

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._tick()

    def _get_actual_stream_info(self) -> str:
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 0.0

        # fourcc -> string
        f = int(self.cap.get(cv2.CAP_PROP_FOURCC) or 0)
        fourcc = "".join([chr((f >> 8 * i) & 0xFF) for i in range(4)])
        fourcc = fourcc if fourcc.strip("\x00").strip() else "N/A"

        req = []
        if self.width and self.height:
            req.append(f"REQ {self.width}x{self.height}")
        if self.fps:
            req.append(f"REQ_FPS {self.fps}")
        if self.fourcc:
            req.append(f"REQ_FMT {self.fourcc.upper()}")
        req_txt = (" | " + " ".join(req)) if req else ""

        return f"CAP {w}x{h} @{fps:.1f}fps | FMT {fourcc} | BACKEND {self.backend.upper()}{req_txt}"

    @staticmethod
    def _overlay_info(frame_bgr, lines: list[str]):
        # 画面叠字：确保用户能“肉眼看到”实际分辨率
        y = 28
        for line in lines:
            cv2.putText(
                frame_bgr,
                line,
                (12, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 0),
                4,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame_bgr,
                line,
                (12, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            y += 26

    def _tick(self):
        if self.cap is None:
            return

        ok, frame = self.cap.read()
        if ok and frame is not None:
            self.last_frame_bgr = frame

            # 用“真实帧尺寸”判断是否真 4K（比 CAP_PROP 更可靠）
            real_h, real_w = frame.shape[:2]
            info1 = f"FRAME {real_w}x{real_h}"
            info2 = self._get_actual_stream_info()
            self._overlay_info(frame, [info1, info2])

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            # 让画面适配窗口大小
            w = self.video_label.winfo_width()
            h = self.video_label.winfo_height()
            if w > 10 and h > 10:
                img = img.resize((w, h), Image.Resampling.BILINEAR)

            photo = ImageTk.PhotoImage(img)
            self._photo_ref = photo  # 防止被 GC
            self.video_label.configure(image=photo)
        else:
            self.status_var.set("读取画面失败：请检查摄像头占用/权限")

        # 每隔一会刷新一次状态栏，避免一直刷屏
        self._tick_count += 1
        if self.cap is not None and self._tick_count % 10 == 0:
            self.status_var.set(self._get_actual_stream_info())

        # 约 30fps
        self.root.after(33, self._tick)

    def capture(self):
        if self.last_frame_bgr is None:
            messagebox.showwarning("提示", "当前没有可用画面，无法拍照。")
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        save_path = self.out_dir / f"{ts}.jpg"
        try:
            _safe_imwrite(save_path, self.last_frame_bgr)
        except Exception as e:
            messagebox.showerror("保存失败", str(e))
            return

        self.status_var.set(f"已保存: {save_path}")

    def close(self):
        try:
            if self.cap is not None:
                self.cap.release()
        finally:
            self.cap = None
            self.root.destroy()

    def run(self):
        self.root.mainloop()


def _open_capture(camera_id: int, backend: str):
    backend_map = {
        "any": cv2.CAP_ANY,
        "dshow": cv2.CAP_DSHOW,
        "msmf": cv2.CAP_MSMF,
    }
    api = backend_map.get(backend.lower())
    if api is None:
        raise ValueError("backend 只能是: any / dshow / msmf")
    return cv2.VideoCapture(camera_id, api)


def _try_mode(camera_id: int, backend: str, fourcc: str | None, width: int, height: int, fps: int | None):
    cap = _open_capture(camera_id, backend)
    try:
        if not cap.isOpened():
            return None

        if fourcc:
            code = cv2.VideoWriter_fourcc(*fourcc.upper())
            cap.set(cv2.CAP_PROP_FOURCC, float(code))

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(width))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(height))
        if fps:
            cap.set(cv2.CAP_PROP_FPS, float(fps))

        if fourcc:
            code = cv2.VideoWriter_fourcc(*fourcc.upper())
            cap.set(cv2.CAP_PROP_FOURCC, float(code))

        # 给驱动一点时间切换模式
        time.sleep(0.15)

        ok, frame = cap.read()
        if not ok or frame is None:
            return None
        h, w = frame.shape[:2]
        return (w, h)
    finally:
        cap.release()


def probe_camera(camera_id: int, backend: str):
    # 从大到小尝试，能直观看出是否支持 4K
    # 组合不要太多，否则部分驱动切换会非常慢，看起来像“卡住”
    resolutions = [
        (3840, 2160),
        (2560, 1440),
        (1920, 1080),
        (1280, 720),
        (640, 480),
    ]
    fmts = ["MJPG", "H264", "YUY2", None]
    fps_list = [30, None]

    seen = set()
    results = []
    total = len(fmts) * len(fps_list) * len(resolutions)
    idx = 0
    print("=== Camera Probe (quick) ===", flush=True)
    print(f"CameraID: {camera_id} | Backend: {backend.upper()}", flush=True)
    print(f"Attempts: {total} (fmt x fps x res)", flush=True)
    for fmt in fmts:
        for fps in fps_list:
            for (w, h) in resolutions:
                idx += 1
                print(f"[{idx:02d}/{total:02d}] try fmt={fmt or 'AUTO'} fps={fps or 'AUTO'} req={w}x{h} ...", flush=True)
                actual = _try_mode(camera_id, backend, fmt, w, h, fps)
                key = (backend.upper(), fmt or "AUTO", fps or 0, w, h, actual)
                if key in seen:
                    continue
                seen.add(key)
                if actual is None:
                    continue
                results.append((backend.upper(), fmt or "AUTO", fps or 0, w, h, actual[0], actual[1]))

    # 去重并按实际分辨率排序
    uniq_actual = sorted({(r[0], r[1], r[2], r[5], r[6]) for r in results}, key=lambda x: (x[3], x[4]), reverse=True)

    print("=== Camera Probe Results ===", flush=True)
    if not uniq_actual:
        print("No frames captured. The camera may be busy or inaccessible.", flush=True)
        return

    print("Captured modes (ACTUAL):", flush=True)
    for b, f, fps, aw, ah in uniq_actual:
        fps_txt = f"{fps}fps" if fps else "fps?"
        print(f"- {aw}x{ah} | fmt={f} | {fps_txt} | backend={b}", flush=True)
    print("Tip: If 3840x2160 never appears here, OpenCV cannot get 4K from this device/driver via this backend.", flush=True)


def parse_args(argv):
    p = argparse.ArgumentParser(description="摄像头实时预览 + 按钮拍照（用于调试摄像头）")
    p.add_argument("--camera-id", type=int, default=0, help="摄像头ID（常见：0/1/2）")
    p.add_argument("--out-dir", type=str, default="camera_captures", help="照片保存目录（相对/绝对路径）")
    p.add_argument("--width", type=int, default=None, help="期望宽度（可选）")
    p.add_argument("--height", type=int, default=None, help="期望高度（可选）")
    p.add_argument("--fps", type=int, default=None, help="期望帧率（可选）")
    p.add_argument("--fourcc", type=str, default="MJPG", help="编码格式（常见：MJPG/H264/YUY2）。默认 MJPG")
    p.add_argument("--backend", type=str, default="dshow", help="视频后端：dshow/msmf/any。默认 dshow")
    p.add_argument("--probe", action="store_true", help="探测可用分辨率/编码并退出（不启动GUI）")
    p.add_argument("--title", type=str, default="摄像头预览", help="窗口标题")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = Path(__file__).resolve().parent / out_dir

    if args.probe:
        probe_camera(args.camera_id, args.backend)
        return

    app = CameraApp(
        camera_id=args.camera_id,
        out_dir=out_dir,
        width=args.width,
        height=args.height,
        fps=args.fps,
        fourcc=args.fourcc,
        backend=args.backend,
        window_title=args.title,
    )
    app.run()


if __name__ == "__main__":
    main()

