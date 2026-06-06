<template>
	<view class="page">
		<!-- 导航栏 -->
		<view class="navbar">
			<view class="navbar-inner">
				<view class="navbar-left" @click="goBack">
					<view class="back-arrow"></view>
				</view>
				<view class="navbar-center">
					<text class="navbar-title">MRI 报告预览</text>
					<text class="navbar-sub">Report Preview</text>
				</view>
				<view class="navbar-right">
					<view class="eye-toggle" @click="change_eye_status">
						<view class="eye-icon-css" :class="{ closed: !name_display }"></view>
					</view>
				</view>
			</view>
		</view>

		<scroll-view scroll-y class="scroll-area" :style="{ height: scrollHeight }">
			<!-- 报告卡片 -->
			<view class="report-wrap" id="pagePoster">
				<view class="report-card">
					<!-- 报告头部 -->
					<view class="report-header">
						<view class="report-header-bg"></view>
						<view class="report-header-content">
							<view class="hospital-badge">
								<text class="hospital-badge-icon">+</text>
							</view>
							<text class="hospital-name">天津市第一人民医院</text>
							<text class="report-type">MRI 检查报告单</text>
						</view>
					</view>

					<!-- 患者信息 -->
					<view class="report-body">
						<view class="info-grid">
							<view class="info-cell">
								<text class="info-key">患者号</text>
								<text class="info-val">{{ patient.pat_id }}</text>
							</view>
							<view class="info-cell">
								<text class="info-key">检查日期</text>
								<text class="info-val">{{ patient.check_time }}</text>
							</view>
						</view>

						<view class="info-divider"></view>

						<view class="info-grid info-grid-3">
							<view class="info-cell">
								<text class="info-key">姓名</text>
								<text class="info-val">{{ name_display ? patient.name : maskName(patient.name) }}</text>
							</view>
							<view class="info-cell">
								<text class="info-key">性别</text>
								<text class="info-val">{{ patient.gender }}</text>
							</view>
							<view class="info-cell">
								<text class="info-key">年龄</text>
								<text class="info-val">{{ patient.age }} 岁</text>
							</view>
						</view>

						<view class="info-row-single">
							<text class="info-key">住院号</text>
							<text class="info-val">{{ patient.host_id }}</text>
						</view>

						<view class="info-grid">
							<view class="info-cell">
								<text class="info-key">科室</text>
								<text class="info-val">{{ patient.department }}</text>
							</view>
							<view class="info-cell">
								<text class="info-key">床号</text>
								<text class="info-val">{{ patient.bed_num }}</text>
							</view>
						</view>

						<view class="info-row-single">
							<text class="info-key">报告日期</text>
							<text class="info-val">{{ patient.report_time }}</text>
						</view>

						<view class="info-divider"></view>

						<view class="info-row-single">
							<text class="info-key">检查项目</text>
							<text class="info-val">{{ patient.check_project }} · {{ patient.position }}</text>
						</view>
					</view>

					<!-- MRI 图像 -->
					<view class="report-image-section" v-if="ct_pic_result_url">
						<image :src="ct_pic_result_url" class="mri-image" mode="aspectFit"></image>
					</view>
					<view class="report-image-section empty-image" v-else>
						<view class="empty-img-icon">
							<text class="empty-img-text">MRI</text>
						</view>
						<text class="empty-img-hint">暂无 AI 分割结果图</text>
					</view>

					<!-- 影像结果 -->
					<view class="report-body">
						<view class="result-block">
							<text class="result-block-title">影像结果</text>
							<text class="result-block-text">{{ imaging_finding_result }}</text>
						</view>

						<!-- 影像诊断 -->
						<view class="diagnosis-block">
							<view class="diagnosis-bar"></view>
							<view class="diagnosis-content">
								<text class="diagnosis-title">影像诊断</text>
								<text class="diagnosis-text">{{ imaging_diagnosis_result }}</text>
							</view>
						</view>

						<view class="info-divider"></view>

						<!-- 医师签名 -->
						<view class="signature-row">
							<view class="sig-item">
								<text class="sig-label">报告医师</text>
								<text class="sig-name">{{ doctor[0] }}</text>
							</view>
							<view class="sig-divider"></view>
							<view class="sig-item">
								<text class="sig-label">审核医师</text>
								<text class="sig-name">{{ doctor[1] }}</text>
							</view>
						</view>
					</view>
				</view>
			</view>

			<!-- 操作按钮 -->
			<view class="actions">
				<view class="action-btn action-share" @click="shareReport">
					<text class="action-btn-text">分享报告</text>
				</view>
				<view class="action-btn action-download" @click="downloadReport">
					<text class="action-btn-text">下载报告</text>
				</view>
			</view>

			<view style="height: 120px;"></view>
		</scroll-view>

		<bottom-nav-doctor current="scan"></bottom-nav-doctor>
	</view>
</template>

<script>
import BottomNavDoctor from '@/components/bottom_nav/BottomNavDoctor.vue'

export default {
	components: { BottomNavDoctor },
	data() {
		return {
			patient: {
				pat_id: '00977851',
				check_time: '2024-10-11 10:02',
				name: '李锦阳',
				gender: '男',
				age: 51,
				host_id: '17102417',
				department: '神经重症医学科(NICU)',
				bed_num: 18,
				report_time: '2024-10-11 15:30',
				check_project: '头颅MRI平扫',
				position: '105层',
			},
			imaging_finding_result: '脑干见多发不规则高密度影，边界不清；余脑实质密度未见异常，脑沟、池稍增宽，脑室未见扩大，中线结构无移位。颅骨未见异常。',
			imaging_diagnosis_result: '1. 脑干出血；2. 建议结合临床进一步检查。',
			doctor: ['曾庆琳', '曾庆琳'],
			ct_pic_result_url: '',
			name_display: false,
			scrollHeight: '100vh'
		}
	},
	onLoad() {
		const sys = uni.getSystemInfoSync()
		this.scrollHeight = (sys.windowHeight - 50) + 'px'
	},
	methods: {
		goBack() {
			uni.navigateBack()
		},
		change_eye_status() {
			this.name_display = !this.name_display
		},
		maskName(name) {
			if (!name || name.length < 2) return '***'
			return '*' + name.substring(1)
		},
		shareReport() {
			uni.showActionSheet({
				itemList: ['分享到微信', '分享到QQ', '复制链接'],
				success: () => {
					uni.showToast({ title: '分享功能开发中', icon: 'none' })
				}
			})
		},
		downloadReport() {
			uni.showLoading({ title: '生成中...' })
			setTimeout(() => {
				uni.hideLoading()
				uni.showToast({ title: '下载功能开发中', icon: 'none' })
			}, 1000)
		}
	}
}
</script>

<style scoped>
.page {
	min-height: 100vh;
	background: var(--ds-bg);
	position: relative;
	overflow: hidden;
}
.scroll-area {
	position: relative;
	z-index: 1;
}

/* 导航栏 */
.navbar {
	position: relative;
	z-index: 10;
	padding: 48px 16px 14px;
	background: rgba(244,246,251,0.85);
	backdrop-filter: saturate(180%) blur(20px);
	-webkit-backdrop-filter: saturate(180%) blur(20px);
	border-bottom: 1px solid var(--ds-hairline);
}
.navbar-inner { display: flex; align-items: center; }
.navbar-left {
	width: 36px; height: 36px;
	border-radius: 10px;
	background: var(--ds-bg-sunken);
	display: flex;
	align-items: center;
	justify-content: center;
}
.navbar-left:active { background: var(--ds-brand-ghost); }
.back-arrow {
	width: 10px; height: 10px;
	border-left: 2px solid var(--ds-ink-3);
	border-bottom: 2px solid var(--ds-ink-3);
	transform: rotate(45deg);
	margin-left: 3px;
}
.navbar-center { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 2px; }
.navbar-title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); }
.navbar-sub { font-size: 11px; color: var(--ds-ink-4); }
.navbar-right { width: 36px; }
.eye-toggle {
	width: 36px; height: 36px;
	border-radius: 10px;
	background: var(--ds-bg-sunken);
	display: flex;
	align-items: center;
	justify-content: center;
}
.eye-toggle:active { background: var(--ds-brand-ghost); }
.eye-icon-css {
	width: 18px; height: 12px;
	border: 2px solid var(--ds-ink-3);
	border-radius: 50%;
	position: relative;
}
.eye-icon-css::after {
	content: '';
	position: absolute;
	top: 2px; left: 5px;
	width: 5px; height: 5px;
	background: var(--ds-ink-3);
	border-radius: 50%;
}
.eye-icon-css.closed { border-color: var(--ds-ink-4); }
.eye-icon-css.closed::after { background: var(--ds-ink-4); }

/* 报告卡片 */
.report-wrap { padding: 20px; }
.report-card {
	background: var(--ds-surface);
	border: 1px solid var(--ds-hairline);
	border-radius: 20px;
	overflow: hidden;
	box-shadow: var(--ds-shadow-md);
}

/* 报告头部 */
.report-header { position: relative; padding: 30px 20px; overflow: hidden; }
.report-header-bg {
	position: absolute;
	top: 0; left: 0; right: 0; bottom: 0;
	background: linear-gradient(135deg, rgba(0,194,215,0.10), rgba(10,92,255,0.06));
}
.report-header-content {
	position: relative; z-index: 1;
	display: flex; flex-direction: column; align-items: center; gap: 8px;
}
.hospital-badge {
	width: 40px; height: 40px;
	border-radius: 50%;
	background: var(--ds-cyan-soft);
	border: 1px solid rgba(0,194,215,0.25);
	display: flex; align-items: center; justify-content: center;
	margin-bottom: 4px;
}
.hospital-badge-icon { font-size: 22px; font-weight: 700; color: var(--ds-cyan); }
.hospital-name { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); }
.report-type { font-size: 13px; color: var(--ds-ink-3); }

/* 报告正文 */
.report-body { padding: 20px; }
.info-grid { display: flex; gap: 16px; margin-bottom: 14px; }
.info-grid-3 { gap: 12px; }
.info-cell { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.info-key { font-size: 11px; color: var(--ds-ink-4); text-transform: uppercase; letter-spacing: 0.5px; }
.info-val { font-size: 14px; font-weight: 500; color: var(--ds-ink-1); }
.info-row-single { display: flex; flex-direction: column; gap: 4px; margin-bottom: 14px; }
.info-divider { height: 1px; background: var(--ds-hairline); margin: 16px 0; }

/* MRI 图像 */
.report-image-section {
	margin: 0 20px 20px;
	background: var(--ds-bg-sunken);
	border: 1px solid var(--ds-hairline);
	border-radius: 14px;
	padding: 16px;
	display: flex;
	justify-content: center;
}
.mri-image { width: 100%; max-height: 240px; border-radius: 10px; }
.empty-image { flex-direction: column; align-items: center; gap: 12px; min-height: 140px; border-style: dashed; }
.empty-img-icon {
	width: 50px; height: 50px;
	border-radius: 50%;
	background: var(--ds-surface);
	border: 1px solid var(--ds-hairline);
	display: flex; align-items: center; justify-content: center;
}
.empty-img-text { font-size: 12px; font-weight: 700; color: var(--ds-ink-3); letter-spacing: 1px; }
.empty-img-hint { font-size: 13px; color: var(--ds-ink-4); }

/* 影像结果 */
.result-block { margin-bottom: 20px; }
.result-block-title {
	display: block; font-size: 13px; font-weight: 600;
	color: var(--ds-ink-4); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;
}
.result-block-text { font-size: 14px; color: var(--ds-ink-2); line-height: 1.8; }

/* 影像诊断 */
.diagnosis-block {
	display: flex; gap: 14px; margin-bottom: 20px; padding: 16px;
	background: rgba(255,107,107,0.05);
	border-radius: 12px;
	border: 1px solid rgba(255,107,107,0.12);
}
.diagnosis-bar {
	width: 3px; border-radius: 2px;
	background: linear-gradient(180deg, #FF6B6B, #FF4757);
	flex-shrink: 0;
}
.diagnosis-content { flex: 1; }
.diagnosis-title { display: block; font-size: 13px; font-weight: 600; color: #FF6B6B; margin-bottom: 8px; }
.diagnosis-text { font-size: 14px; color: var(--ds-ink-2); line-height: 1.8; }

/* 签名 */
.signature-row { display: flex; align-items: center; padding-top: 4px; }
.sig-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; }
.sig-label { font-size: 11px; color: var(--ds-ink-4); }
.sig-name { font-size: 15px; font-weight: 600; color: var(--ds-ink-1); }
.sig-divider { width: 1px; height: 30px; background: var(--ds-hairline); margin: 0 16px; }

/* 操作按钮 */
.actions { display: flex; gap: 12px; padding: 0 20px; margin-top: 8px; }
.action-btn {
	flex: 1; padding: 16px; border-radius: 14px;
	display: flex; align-items: center; justify-content: center;
	transition: all 0.3s;
}
.action-btn:active { transform: scale(0.97); }
.action-share { background: var(--ds-grad-brand); }
.action-download { background: var(--ds-bg-sunken); border: 1px solid var(--ds-hairline); }
.action-btn-text { font-size: 15px; font-weight: 600; color: #fff; }
.action-download .action-btn-text { color: var(--ds-ink-2); }
</style>
