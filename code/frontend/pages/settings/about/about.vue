<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack" hover-class="back-pressed">
					<text class="back-char">‹</text>
				</view>
				<text class="nav-title">关于我们</text>
				<view class="nav-placeholder"></view>
			</view>
		</view>

		<view class="content">
			<!-- Logo + 名称 -->
			<view class="brand-area ds-rise ds-d1">
				<view class="brand-logo ds-scanline">
					<image class="brand-img" src="/static/logo.png" mode="aspectFit"></image>
				</view>
				<text class="brand-name">BraiLink</text>
				<view class="brand-sub-row">
					<view class="sub-line"></view>
					<text class="brand-sub ds-mono">VERSION 1.0.0</text>
					<view class="sub-line"></view>
				</view>
			</view>

			<!-- 简介 -->
			<view class="card ds-rise ds-d2">
				<view class="card-head">
					<text class="card-title">系统简介</text>
					<text class="card-sub ds-mono">INTRODUCTION</text>
				</view>
				<text class="card-text">BraiLink 是一款基于人工智能技术的医疗辅助诊断软件，致力于为医生提供准确、高效的脑瘤 MRI 影像分析服务。系统采用先进的深度学习算法，可自动识别和分割脑瘤区域，辅助医生进行诊断决策。</text>
			</view>

			<!-- 功能 -->
			<view class="card ds-rise ds-d3">
				<view class="card-head">
					<text class="card-title">主要功能</text>
					<text class="card-sub ds-mono">CAPABILITIES</text>
				</view>
				<view class="feature-list">
					<view class="feature-item" v-for="(feature, index) in features" :key="index">
						<view class="feature-num ds-mono">0{{ index + 1 }}</view>
						<text class="feature-text">{{ feature }}</text>
					</view>
				</view>
			</view>

			<!-- 团队 -->
			<view class="card ds-rise ds-d4">
				<view class="card-head">
					<text class="card-title">开发团队</text>
					<text class="card-sub ds-mono">THE TEAM</text>
				</view>
				<text class="card-text">本系统由专业的医疗 AI 研发团队开发，团队成员包括医学专家、AI 算法工程师和软件开发工程师，致力于将先进的 AI 技术应用于医疗诊断领域。</text>
			</view>

			<!-- 联系 -->
			<view class="card ds-rise ds-d5">
				<view class="card-head">
					<text class="card-title">联系我们</text>
					<text class="card-sub ds-mono">CONTACT</text>
				</view>
				<view class="contact-list">
					<view class="contact-item">
						<view class="contact-ico">
							<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#0A5CFF" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>
						</view>
						<text class="contact-label ds-mono">EMAIL</text>
						<text class="contact-value">support@brailink.com</text>
					</view>
					<view class="contact-item">
						<view class="contact-ico">
							<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#0A5CFF" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
						</view>
						<text class="contact-label ds-mono">PHONE</text>
						<text class="contact-value">400-123-4567</text>
					</view>
					<view class="contact-item">
						<view class="contact-ico">
							<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#0A5CFF" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
						</view>
						<text class="contact-label ds-mono">ADDR</text>
						<text class="contact-value">中国 · 广州市天河区智慧医疗园区</text>
					</view>
				</view>
			</view>

			<view class="copyright ds-rise ds-d5">
				<view class="pulse-dot"></view>
				<text class="copyright-text ds-mono">© 2026 BraiLink · ALL RIGHTS RESERVED</text>
			</view>
			<view style="height: 30px;"></view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			features: [
				'智能 MRI 图像分析与肿瘤识别',
				'自动化脑瘤区域分割',
				'AI 辅助诊断报告生成',
				'患者病历管理系统',
				'医患在线咨询服务'
			]
		}
	},
	methods: {
		goBack() { uni.navigateBack({ delta: 1 }) }
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); font-family: var(--ds-font); }
.navbar { position: sticky; top: 0; z-index: 100; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.82); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; display: flex; align-items: center; justify-content: space-between; padding: 52px 16px 12px; }
.nav-back { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
.back-pressed { background: var(--ds-brand-ghost); }
.back-char { font-size: 32px; font-weight: 300; color: var(--ds-brand); line-height: 1; margin-top: -4px; }
.nav-title { font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-placeholder { width: 36px; }

.content { padding: 24px 20px 0; }
.brand-area { display: flex; flex-direction: column; align-items: center; padding: 8px 0 32px; }
.brand-logo { --ds-scan-h: 90px; width: 90px; height: 90px; border-radius: 24px; background: var(--ds-surface); box-shadow: var(--ds-shadow-md); display: flex; align-items: center; justify-content: center; overflow: hidden; margin-bottom: 14px; }
.brand-img { width: 84px; height: 84px; }
.brand-name { font-size: 24px; font-weight: 800; color: var(--ds-ink-1); letter-spacing: 2px; margin-bottom: 8px; }
.brand-sub-row { display: flex; align-items: center; gap: 8px; }
.sub-line { width: 18px; height: 1px; background: var(--ds-ink-4); }
.brand-sub { font-size: 10px; font-weight: 600; color: var(--ds-ink-3); letter-spacing: 1.5px; }

.card { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 18px; margin-bottom: 12px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.card-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid var(--ds-hairline); }
.card-title { font-size: 15px; font-weight: 800; color: var(--ds-ink-1); letter-spacing: 0.3px; }
.card-sub { font-size: 10px; font-weight: 600; color: var(--ds-ink-4); letter-spacing: 1px; }
.card-text { font-size: 14px; line-height: 1.7; color: var(--ds-ink-2); }

.feature-list { display: flex; flex-direction: column; gap: 10px; }
.feature-item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); }
.feature-num { font-size: 13px; font-weight: 800; color: var(--ds-brand); letter-spacing: 0.5px; flex-shrink: 0; min-width: 26px; }
.feature-text { font-size: 13px; color: var(--ds-ink-2); flex: 1; }

.contact-list { display: flex; flex-direction: column; gap: 12px; }
.contact-item { display: flex; align-items: center; gap: 10px; }
.contact-ico { width: 28px; height: 28px; border-radius: 8px; background: var(--ds-brand-soft); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.contact-label { font-size: 10px; font-weight: 700; color: var(--ds-ink-4); letter-spacing: 1px; min-width: 42px; }
.contact-value { font-size: 13px; color: var(--ds-ink-2); flex: 1; }

.copyright { display: flex; justify-content: center; align-items: center; gap: 8px; padding: 28px 0 0; }
.pulse-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--ds-success); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(31,184,119,0.5); } 70% { box-shadow: 0 0 0 6px rgba(31,184,119,0); } 100% { box-shadow: 0 0 0 0 rgba(31,184,119,0); } }
.copyright-text { font-size: 10px; font-weight: 600; color: var(--ds-ink-3); letter-spacing: 1px; }
</style>
