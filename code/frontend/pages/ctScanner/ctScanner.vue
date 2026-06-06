<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-inner">
				<text class="nav-title">MRI 智能扫描</text>
				<text class="nav-sub">AI-Powered Analysis</text>
			</view>
		</view>

		<scroll-view scroll-y class="scroll-area" :style="{ height: scrollHeight }">
			<!-- 扫描模式 -->
			<view class="section">
				<text class="section-label">扫描模式</text>
				<view class="mode-row">
					<view class="mode-chip" v-for="opt in scanOptions" :key="opt.value" :class="{ active: scan_mode_id === opt.value, disabled: isAnalyzing }" @click="selectMode(opt.value)">
						<text class="mode-code">{{ opt.code }}</text>
					</view>
				</view>
			</view>

			<!-- 本地图像 -->
			<view class="section">
				<text class="section-label">影像采集</text>
				<view class="card upload-card" :class="{ filled: uploadFile.length > 0 }">
					<view class="card-head">
						<text class="card-title">本地图像上传</text>
						<view class="card-badge" v-if="uploadFile.length > 0"><text class="badge-text">已就绪</text></view>
					</view>
					<view class="upload-area" @click="chooseLocalImage">
						<view class="upload-preview" v-if="uploadFile.length > 0">
							<image :src="uploadFile[0].url" class="upload-thumb" mode="aspectFill"></image>
							<view class="upload-remove" @click.stop="removeImage">
								<text class="remove-icon">×</text>
							</view>
						</view>
						<view v-else class="upload-placeholder">
							<view class="upload-icon-ring">
								<text class="upload-icon-text">+</text>
							</view>
							<text class="upload-hint">点击选择 MRI 图像</text>
						</view>
					</view>
				</view>

				<!-- USB 拍照 -->
				<view class="card camera-card" :class="{ filled: capturedImageUrl }">
					<view class="card-head">
						<text class="card-title">USB 硬件采集</text>
						<view class="card-badge blue" v-if="capturedImageUrl"><text class="badge-text">已拍照</text></view>
					</view>
					<view class="camera-row">
						<view class="camera-preview" :class="{ empty: !capturedImageUrl }">
							<image v-if="capturedImageUrl" :src="capturedImageUrl" class="camera-img" mode="aspectFill"></image>
							<view v-else class="cam-empty">
								<view class="cam-ring" :class="{ pulse: !isCapturing }">
									<text class="cam-text">CAM</text>
								</view>
							</view>
						</view>
						<view class="camera-info">
							<text class="cam-title">{{ capturedImageUrl ? '硬件采集图' : '相机编号 1' }}</text>
							<text class="cam-desc">{{ capturedImageUrl ? capturedImageName : '点击按钮后自动拍照并分析' }}</text>
						</view>
					</view>
					<view class="capture-btn" :class="{ disabled: isAnalyzing || isCapturing }" @click="captureAndAnalyze">
						<view class="capture-spinner" v-if="isCapturing"></view>
						<text class="capture-text">{{ isCapturing ? '设备指令下发中...' : '启动硬件拍照' }}</text>
					</view>
				</view>
			</view>

			<!-- 分析按钮 -->
			<view class="section action-section">
				<view class="analyze-btn" :class="{ disabled: !canAnalyze, running: isAnalyzing }" @click="ctScan">
					<view class="analyze-spinner" v-if="isAnalyzing"></view>
					<text class="analyze-text">{{ isAnalyzing ? 'AI 分析中...' : '开始 AI 分析' }}</text>
				</view>
			</view>

			<!-- 分割结果 -->
			<view class="section result-section" v-if="tumorPicList" :class="{ reveal: resultRevealed }">
				<text class="section-label">分割结果</text>
				<view class="result-card">
					<image :src="tumorPicList" class="result-image" mode="aspectFit"></image>
				</view>
			</view>

			<!-- 分析报告 -->
			<view class="section report-section" v-if="analysisResult" :class="{ reveal: resultRevealed }">
				<text class="section-label">AI 分析报告</text>

				<view class="status-card" :class="analysisResult.tumor_detected ? 'danger' : 'safe'">
					<view class="status-icon-box" :class="analysisResult.tumor_detected ? 'danger' : 'safe'">
						<text class="status-icon-text">{{ analysisResult.tumor_detected ? '!' : '✓' }}</text>
					</view>
					<view class="status-info">
						<text class="status-label">{{ analysisResult.tumor_detected ? '检测到肿瘤区域' : '未检测到肿瘤' }}</text>
						<text class="status-sub">{{ getScanModeLabel() }} · {{ getConfidenceText() }}</text>
					</view>
				</view>

				<view class="metric-card">
					<view class="metric-row"><text class="metric-label">置信度</text><text class="metric-value">{{ getConfidenceText() }}</text></view>
					<view class="bar-track"><view class="bar-fill" :class="analysisResult.tumor_detected ? 'fill-danger' : 'fill-safe'" :style="{ width: confidenceAnimated + '%' }"></view></view>
				</view>

				<view class="metric-card" v-if="analysisResult.tumor_detected">
					<view class="stat-row">
						<view class="stat-cell"><text class="stat-num">{{ analysisResult.tumor_area || 0 }}</text><text class="stat-unit">像素面积</text></view>
						<view class="stat-divider"></view>
						<view class="stat-cell"><text class="stat-num">{{ analysisResult.tumor_regions_count || 0 }}</text><text class="stat-unit">肿瘤区域</text></view>
						<view class="stat-divider"></view>
						<view class="stat-cell"><text class="stat-num">{{ getScanModeLabel() }}</text><text class="stat-unit">扫描模式</text></view>
					</view>
				</view>

				<view class="metric-card" v-if="analysisResult.tumor_detected && hasClassStats">
					<text class="card-label">组织分类统计</text>
					<view class="tissue-item" v-for="(stats, className) in analysisResult.class_statistics" :key="className">
						<view class="tissue-head">
							<view class="tissue-dot" :class="getClassColor(className)"></view>
							<text class="tissue-name">{{ className }}</text>
							<text class="tissue-pct">{{ stats.percentage.toFixed(1) }}%</text>
						</view>
						<view class="tissue-track"><view class="tissue-fill" :class="getClassColor(className)" :style="{ width: stats.percentage + '%' }"></view></view>
					</view>
				</view>

				<view class="metric-card" v-if="analysisResult.analysis">
					<text class="card-label">详细分析</text>
					<text class="detail-text">{{ analysisResult.analysis }}</text>
				</view>
			</view>

			<view style="height: 120px;"></view>
		</scroll-view>

		<!-- AI 分析蒙层 -->
		<view class="overlay" v-if="isAnalyzing" @touchmove.stop.prevent>
			<view class="overlay-panel">
				<view class="ring-wrap">
					<view class="ring r1"></view>
					<view class="ring r2"></view>
					<view class="ring r3"></view>
					<view class="ring-core"><text class="ring-text">AI</text></view>
				</view>
				<text class="overlay-title">脑瘤 MRI 分割分析</text>
				<text class="overlay-stage">{{ analysisStageText }}</text>
				<view class="stage-bar">
					<view class="stage-item" v-for="(s, i) in stages" :key="i" :class="{ done: analysisStage > i, active: analysisStage === i }">
						<view class="stage-dot"></view>
						<text class="stage-label">{{ s }}</text>
					</view>
					<view class="stage-line"><view class="stage-line-fill" :style="{ width: stageProgressPercent + '%' }"></view></view>
				</view>
			</view>
		</view>

		<bottom-nav-doctor current="scan"></bottom-nav-doctor>
		<u-toast ref="uToast" />
	</view>
</template>

<script>
import BottomNavDoctor from '@/components/bottom_nav/BottomNavDoctor.vue'
import { mlAPI, API_CONFIG } from '@/utils/request.js'

export default {
	components: { BottomNavDoctor },
	data() {
		return {
			scanOptions: [{ code: 'T1', value: 't1' }, { code: 'T2', value: 't2' }, { code: 'T1CE', value: 't1ce' }, { code: 'FLAIR', value: 'flair' }],
			scan_mode_id: '', tumorPicList: '', uploadFile: [], analysisResult: null,
			isAnalyzing: false, isCapturing: false, cameraId: 1, capturedImageUrl: '', capturedImageName: '',
			scrollHeight: '100vh', analysisStage: 0, stages: ['图像预处理', '模型推理', '结果生成'], confidenceAnimated: 0, resultRevealed: false
		}
	},
	computed: {
		canAnalyze() { return this.scan_mode_id && this.uploadFile.length > 0 && !this.isAnalyzing },
		analysisStageText() { if (this.analysisStage >= 3) return '分析完成'; return this.stages[this.analysisStage] || '准备中...' },
		stageProgressPercent() { if (this.analysisStage >= 3) return 100; return Math.min(Math.round((this.analysisStage / 3) * 100) + 5, 100) },
		hasClassStats() { const cs = this.analysisResult?.class_statistics; return cs && typeof cs === 'object' && Object.keys(cs).length > 0 }
	},
	onLoad() { const s = uni.getSystemInfoSync(); this.scrollHeight = (s.windowHeight - 50) + 'px' },
	methods: {
		chooseLocalImage() {
				if (this.isAnalyzing || this.uploadFile.length > 0) return
				// 优先使用 uni.chooseMedia（新版API），降级使用 uni.chooseImage
				const chooseFn = uni.chooseMedia ? uni.chooseMedia : uni.chooseImage
				const opts = uni.chooseMedia
					? { count: 1, mediaType: ['image'], sourceType: ['album', 'camera'], sizeType: ['original'] }
					: { count: 1, sourceType: ['album', 'camera'], sizeType: ['original'] }
				chooseFn({
					...opts,
					success: (res) => {
						const filePath = res.tempFiles?.[0]?.tempFilePath || res.tempFilePaths?.[0]
						if (filePath) {
							this.uploadFile = [{ url: filePath }]
							this.tumorPicList = ''
							this.analysisResult = null
							this.capturedImageUrl = ''
							this.resultRevealed = false
							this.confidenceAnimated = 0
							// 自动选择默认扫描模式
							if (!this.scan_mode_id) this.scan_mode_id = 't1ce'
						}
					},
					fail: (err) => {
						if (err.errMsg && err.errMsg.includes('cancel')) return
						uni.showToast({ title: '选择图片失败', icon: 'none' })
					}
				})
			},
			removeImage() {
				this.uploadFile = []
				this.tumorPicList = ''
				this.analysisResult = null
				this.resultRevealed = false
				this.confidenceAnimated = 0
			},
			selectMode(v) { if (!this.isAnalyzing) this.scan_mode_id = v },
		isScanModeMissing() { return !this.scan_mode_id },
		resolveMediaUrl(p) { if (!p) return ''; if (p.startsWith('http')) return p; return `${API_CONFIG.BASE_URL}${p}` },
		async ctScan() {
			if (this.isScanModeMissing()) { uni.showToast({ title: '请先选择扫描模式', icon: 'none' }); return }
			if (!this.uploadFile.length) { uni.showToast({ title: '请先上传 MRI 图像', icon: 'none' }); return }
			if (this.isAnalyzing) return
			this.isAnalyzing = true; this.resultRevealed = false; this.confidenceAnimated = 0; this.analysisStage = 0
			const t = setInterval(() => { if (this.analysisStage < 2) this.analysisStage++ }, 2500)
			try {
				console.log('[ctScan] 开始分析, imagePath:', this.uploadFile[0].url, 'scanMode:', this.scan_mode_id)
				const r = await mlAPI.analyzeCT({ imagePath: this.uploadFile[0].url, scanMode: this.scan_mode_id })
				console.log('[ctScan] 后端返回:', JSON.stringify(r))
				clearInterval(t); this.analysisStage = 3
				if (r.success) { this.analysisResult = r.result; this.tumorPicList = r.result.processed_image ? this.resolveMediaUrl(r.result.processed_image) : this.uploadFile[0].url; setTimeout(() => { this.isAnalyzing = false; this.resultRevealed = true; this.animateConfidence(r.result.confidence_score) }, 600) }
				else { this.isAnalyzing = false; uni.showToast({ title: r.error || '分析失败', icon: 'none', duration: 3000 }) }
			} catch (e) { console.error('[ctScan] 异常:', e); clearInterval(t); this.isAnalyzing = false; uni.showToast({ title: e.message || '分析失败', icon: 'none', duration: 3000 }) }
		},
		async captureAndAnalyze() {
			if (this.isScanModeMissing()) { this.$refs.uToast.show({ title: '请先选择扫描模式', type: 'warning' }); return }
			if (this.isAnalyzing || this.isCapturing) return
			this.isCapturing = true; this.isAnalyzing = true; this.resultRevealed = false; this.confidenceAnimated = 0; this.analysisStage = 0
			const t = setInterval(() => { if (this.analysisStage < 2) this.analysisStage++ }, 3000)
			try {
				const r = await mlAPI.captureCamera({ camera_id: this.cameraId, delay: 1.0, warmup_frames: 18, scan_mode: this.scan_mode_id })
				clearInterval(t); this.analysisStage = 3
				if (!r.success) { if (r.capture?.image) { this.uploadFile = []; this.analysisResult = null; this.tumorPicList = ''; this.capturedImageUrl = this.resolveMediaUrl(r.capture.image); this.capturedImageName = r.capture.filename || 'camera.jpg' }; this.isCapturing = false; this.isAnalyzing = false; this.$refs.uToast.show({ title: r.error || '未通过医学影像校验', type: 'warning' }); return }
				this.uploadFile = []; this.analysisResult = r.result; this.capturedImageUrl = this.resolveMediaUrl(r.capture?.image); this.capturedImageName = r.capture?.filename || 'camera.jpg'; this.tumorPicList = r.result?.processed_image ? this.resolveMediaUrl(r.result.processed_image) : this.capturedImageUrl
				setTimeout(() => { this.isCapturing = false; this.isAnalyzing = false; this.resultRevealed = true; this.animateConfidence(r.result.confidence_score) }, 600)
			} catch (e) { clearInterval(t); this.isCapturing = false; this.isAnalyzing = false; this.$refs.uToast.show({ title: e.message || '拍照失败', type: 'error' }) }
		},
		animateConfidence(target) { const d = 800, s = performance.now(), to = Math.round((target || 0) * 1000) / 10; const step = (now) => { const p = Math.min((now - s) / d, 1); this.confidenceAnimated = Math.round(to * (1 - Math.pow(1 - p, 3)) * 10) / 10; if (p < 1) requestAnimationFrame(step) }; requestAnimationFrame(step) },
		getScanModeLabel() { return this.scanOptions.find(o => o.value === this.scan_mode_id)?.code || '' },
		getConfidenceText() { return this.analysisResult ? (this.analysisResult.confidence_score * 100).toFixed(1) + '%' : '' },
		getClassColor(n) { return { '坏死核心': 't-necrotic', '水肿区域': 't-edema', '增强肿瘤': 't-enhancing' }[n] || 't-default' }
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); display: flex; flex-direction: column; font-family: var(--ds-font); }
.navbar { padding: 48px 20px 16px; background: rgba(244,246,251,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 0.5px solid var(--ds-hairline); text-align: center; }
.nav-title { display: block; font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-sub { display: block; font-size: 11px; color: var(--ds-ink-4); margin-top: 2px; }
.scroll-area { flex: 1; }

.section { padding: 0 20px; margin-top: 20px; }
.section-label { display: block; font-size: 13px; font-weight: 600; color: var(--ds-ink-3); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px; }

.mode-row { display: flex; gap: 8px; }
.mode-chip { flex: 1; padding: 12px 0; border-radius: 12px; background: var(--ds-surface); border: 1px solid var(--ds-hairline); text-align: center; transition: all 0.2s; }
.mode-chip.active { background: var(--ds-brand-soft); border-color: var(--ds-brand); }
.mode-chip.disabled { opacity: 0.4; pointer-events: none; }
.mode-code { font-size: 16px; font-weight: 600; color: var(--ds-ink-2); }
.mode-chip.active .mode-code { color: var(--ds-brand); }

.card { background: var(--ds-surface); border-radius: 14px; padding: 16px; margin-bottom: 12px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.card.filled { border-color: rgba(10,92,255,0.3); }
.card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-title { font-size: 16px; font-weight: 600; color: var(--ds-ink-1); }
.card-badge { padding: 3px 10px; border-radius: 10px; background: rgba(31,184,119,0.12); }
.card-badge.blue { background: var(--ds-brand-soft); }
.badge-text { font-size: 11px; font-weight: 600; color: var(--ds-success); }
.card-badge.blue .badge-text { color: var(--ds-brand); }

.upload-area { background: var(--ds-surface); border: 1.5px dashed var(--ds-hairline); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 180px; gap: 10px; }
.upload-area:active { background: var(--ds-bg-sunken); }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.upload-icon-ring { width: 56px; height: 56px; border-radius: 50%; border: 2px solid var(--ds-hairline); display: flex; align-items: center; justify-content: center; }
.upload-icon-text { font-size: 28px; color: var(--ds-ink-3); line-height: 1; }
.upload-hint { font-size: 14px; color: var(--ds-ink-4); }
.upload-preview { position: relative; width: 160px; height: 160px; border-radius: 10px; overflow: hidden; }
.upload-thumb { width: 100%; height: 100%; }
.upload-remove { position: absolute; top: 6px; right: 6px; width: 24px; height: 24px; border-radius: 50%; background: rgba(0,0,0,0.55); display: flex; align-items: center; justify-content: center; z-index: 2; }
.remove-icon { font-size: 16px; color: #fff; line-height: 1; }

.camera-row { display: flex; gap: 12px; margin-bottom: 12px; }
.camera-preview { width: 100px; height: 100px; border-radius: 12px; background: var(--ds-bg-sunken); border: 1px solid var(--ds-hairline); overflow: hidden; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.camera-preview.empty { border-style: dashed; }
.camera-img { width: 100%; height: 100%; }
.cam-empty { text-align: center; }
.cam-ring { width: 44px; height: 44px; border-radius: 50%; border: 1.5px solid rgba(10,92,255,0.32); display: flex; align-items: center; justify-content: center; margin: 0 auto; }
.cam-ring.pulse { animation: breathe 2.5s ease-in-out infinite; }
.cam-text { font-size: 11px; font-weight: 700; color: var(--ds-brand); letter-spacing: 1px; }
.camera-info { flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.cam-title { font-size: 14px; font-weight: 500; color: var(--ds-ink-1); }
.cam-desc { font-size: 12px; color: var(--ds-ink-3); }

.capture-btn { border-radius: 12px; padding: 12px; background: var(--ds-brand-soft); display: flex; align-items: center; justify-content: center; gap: 8px; }
.capture-btn:active { opacity: 0.8; }
.capture-btn.disabled { opacity: 0.4; pointer-events: none; }
.capture-spinner { width: 16px; height: 16px; border: 2px solid var(--ds-hairline); border-top-color: var(--ds-cyan); border-radius: 50%; animation: spin 0.7s linear infinite; }
.capture-text { font-size: 15px; font-weight: 500; color: var(--ds-brand); }

.action-section { margin-top: 24px; }
.analyze-btn { border-radius: 14px; padding: 16px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; gap: 8px; }
.analyze-btn:active { opacity: 0.85; }
.analyze-btn.disabled { background: var(--ds-bg-sunken); box-shadow: none; pointer-events: none; }
.analyze-btn.running { background: var(--ds-bg-sunken); box-shadow: none; }
.analyze-text { font-size: 17px; font-weight: 600; color: #fff; }
.analyze-btn.disabled .analyze-text, .analyze-btn.running .analyze-text { color: var(--ds-ink-4); }
.analyze-spinner { width: 18px; height: 18px; border: 2px solid var(--ds-hairline); border-top-color: var(--ds-cyan); border-radius: 50%; animation: spin 0.7s linear infinite; }

.result-section, .report-section { opacity: 0; transform: translateY(24px); transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
.result-section.reveal, .report-section.reveal { opacity: 1; transform: translateY(0); }
.report-section { transition-delay: 0.1s; }
.result-card { border-radius: 14px; overflow: hidden; background: var(--ds-surface); border: 1px solid var(--ds-hairline); }
.result-image { width: 100%; min-height: 200px; }

.status-card { display: flex; align-items: center; gap: 14px; padding: 16px; border-radius: 14px; margin-bottom: 10px; }
.status-card.danger { background: rgba(255,77,94,0.08); }
.status-card.safe { background: rgba(31,184,119,0.08); }
.status-icon-box { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.status-icon-box.danger { background: rgba(255,77,94,0.15); }
.status-icon-box.safe { background: rgba(31,184,119,0.15); }
.status-icon-text { font-size: 18px; font-weight: 700; }
.status-icon-box.danger .status-icon-text { color: var(--ds-danger); }
.status-icon-box.safe .status-icon-text { color: var(--ds-success); }
.status-info { flex: 1; }
.status-label { display: block; font-size: 16px; font-weight: 600; color: var(--ds-ink-1); margin-bottom: 2px; }
.status-sub { font-size: 13px; color: var(--ds-ink-3); }

.metric-card { background: var(--ds-surface); border-radius: 14px; padding: 16px; margin-bottom: 10px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.metric-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.metric-label { font-size: 14px; color: var(--ds-ink-3); }
.metric-value { font-size: 20px; font-weight: 700; color: var(--ds-ink-1); }
.bar-track { height: 4px; background: var(--ds-bg-sunken); border-radius: 2px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 2px; transition: width 0.8s ease; }
.bar-fill.fill-danger { background: #FF3B30; }
.bar-fill.fill-safe { background: #34C759; }

.stat-row { display: flex; }
.stat-cell { flex: 1; text-align: center; padding: 8px 0; }
.stat-divider { width: 0.5px; background: var(--ds-hairline); margin: 4px 0; }
.stat-num { display: block; font-size: 20px; font-weight: 700; color: var(--ds-ink-1); }
.stat-unit { display: block; font-size: 11px; color: var(--ds-ink-4); margin-top: 2px; }

.card-label { display: block; font-size: 14px; font-weight: 600; color: var(--ds-ink-3); margin-bottom: 12px; }
.tissue-item { margin-bottom: 14px; }
.tissue-item:last-child { margin-bottom: 0; }
.tissue-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.tissue-dot { width: 8px; height: 8px; border-radius: 50%; }
.tissue-dot.t-necrotic { background: #FF3B30; }
.tissue-dot.t-edema { background: #34C759; }
.tissue-dot.t-enhancing { background: var(--ds-grad-brand); }
.tissue-dot.t-default { background: #8E8E93; }
.tissue-name { flex: 1; font-size: 14px; color: var(--ds-ink-1); }
.tissue-pct { font-size: 14px; font-weight: 600; color: var(--ds-ink-3); }
.tissue-track { height: 4px; background: var(--ds-bg-sunken); border-radius: 2px; overflow: hidden; }
.tissue-fill { height: 100%; border-radius: 2px; transition: width 0.8s ease; }
.tissue-fill.t-necrotic { background: #FF3B30; }
.tissue-fill.t-edema { background: #34C759; }
.tissue-fill.t-enhancing { background: var(--ds-grad-brand); }
.tissue-fill.t-default { background: #8E8E93; }
.detail-text { font-size: 15px; color: var(--ds-ink-2); line-height: 1.6; }

/* Overlay */
.overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); z-index: 9999; display: flex; align-items: center; justify-content: center; }
.overlay-panel { display: flex; flex-direction: column; align-items: center; gap: 20px; padding: 40px 20px; }
.ring-wrap { width: 100px; height: 100px; position: relative; display: flex; align-items: center; justify-content: center; }
.ring { position: absolute; border-radius: 50%; border: 1px solid rgba(10,92,255,0.18); }
.r1 { width: 100%; height: 100%; animation: ringPulse 3s ease-in-out infinite; }
.r2 { width: 75%; height: 75%; animation: ringPulse 3s ease-in-out 0.5s infinite; }
.r3 { width: 50%; height: 50%; animation: ringPulse 3s ease-in-out 1s infinite; }
.ring-core { width: 48px; height: 48px; border-radius: 50%; background: var(--ds-brand-soft); display: flex; align-items: center; justify-content: center; position: relative; z-index: 1; }
.ring-text { font-size: 16px; font-weight: 700; color: var(--ds-brand); }
.overlay-title { font-size: 20px; font-weight: 600; color: var(--ds-ink-1); }
.overlay-stage { font-size: 15px; color: var(--ds-brand); }

.stage-bar { display: flex; justify-content: space-between; width: 100%; position: relative; padding: 0 10px; }
.stage-item { display: flex; flex-direction: column; align-items: center; gap: 6px; z-index: 1; }
.stage-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--ds-bg-sunken); border: 1.5px solid var(--ds-hairline); transition: all 0.3s; }
.stage-item.active .stage-dot { background: var(--ds-grad-brand); border-color: var(--ds-brand); }
.stage-item.done .stage-dot { background: var(--ds-success); border-color: #1FB877; }
.stage-label { font-size: 10px; color: var(--ds-ink-4); white-space: nowrap; }
.stage-item.active .stage-label { color: var(--ds-brand); font-weight: 500; }
.stage-item.done .stage-label { color: var(--ds-success); }
.stage-line { position: absolute; top: 4px; left: 24px; right: 24px; height: 1px; background: var(--ds-hairline); z-index: 0; }
.stage-line-fill { height: 100%; background: linear-gradient(90deg, var(--ds-brand), var(--ds-success)); transition: width 0.8s ease; }

@keyframes breathe { 0%,100% { box-shadow: 0 0 0 0 rgba(10,92,255,0.28); } 50% { box-shadow: 0 0 0 8px rgba(0,122,255,0); } }
@keyframes ringPulse { 0%,100% { transform: scale(1); opacity: 0.3; } 50% { transform: scale(1.06); opacity: 0.6; } }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
