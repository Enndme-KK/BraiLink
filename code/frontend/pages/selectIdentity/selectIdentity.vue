<template>
	<view class="page ds-page">
		<!-- 顶区:深空蓝阅片灯箱 + 扫描线 -->
		<view class="hero ds-scanline ds-grid-bg">
			<view class="hero-glow"></view>
			<view class="hero-content">
				<view class="logo-box ds-rise ds-d1">
					<!-- 真实 App 图标 + 旋转扫描环 -->
					<view class="logo-ring"></view>
					<image class="logo-img" src="/static/logo.png" mode="aspectFit"></image>
					<view class="logo-dot logo-dot-2"></view>
					<view class="logo-dot logo-dot-3"></view>
				</view>
				<text class="app-title ds-rise ds-d2">BraiLink</text>
				<view class="app-sub-row ds-rise ds-d3">
					<view class="sub-line"></view>
					<text class="app-sub ds-mono">AI-POWERED · BRAIN DIAGNOSIS</text>
					<view class="sub-line"></view>
				</view>
			</view>
		</view>

		<!-- 身份选择 -->
		<view class="section-area">
			<view class="section-head ds-rise ds-d3">
				<text class="section-label">选择身份</text>
				<text class="section-hint">SELECT ROLE</text>
			</view>
			<view class="card-group">
				<view class="card-item ds-rise" :class="'ds-d' + (i + 4 > 5 ? 5 : i + 4)"
					v-for="(card, i) in identityCards" :key="i"
					@click="card.action" hover-class="item-pressed">
					<view class="card-icon" :style="{ background: card.grad }">
						<!-- 线性 SVG 图标,告别字母占位 -->
						<view class="ico" v-html="card.svg"></view>
					</view>
					<view class="card-body">
						<text class="card-title">{{ card.title }}</text>
						<text class="card-desc">{{ card.desc }}</text>
					</view>
					<view class="card-chevron"><view class="chev"></view></view>
				</view>
			</view>
		</view>

		<view class="footer-area ds-rise ds-d5">
			<view class="footer-badge">
				<view class="pulse-dot"></view>
				<text class="footer-text ds-mono">BraiLink · v1.0</text>
			</view>
		</view>
	</view>
</template>

<script>
import { isLoggedIn, getCurrentUserType } from '@/utils/auth.js'

export default {
	data() {
		return {
			identityCards: [
				{
					title: '医生端', desc: '患者管理 · 影像诊断',
					grad: 'linear-gradient(135deg, #0A5CFF 0%, #00C2D7 100%)',
					svg: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v6a6 6 0 0 0 12 0V3"/><path d="M6 3H4M18 3h2M12 15v3a4 4 0 0 0 8 0v-1"/><circle cx="20" cy="14" r="2"/></svg>',
					action: this.toDoctorPage
				},
				{
					title: '患者端', desc: '健康档案 · AI 咨询',
					grad: 'linear-gradient(135deg, #1FB877 0%, #00C2D7 100%)',
					svg: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>',
					action: this.toPatientPage
				},
				{
					title: '家属端', desc: '协助管理 · 查看病历',
					grad: 'linear-gradient(135deg, #F5A623 0%, #FF7A59 100%)',
					svg: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
					action: this.toFamilyPage
				}
			]
		}
	},
	onLoad() { this.checkLoginStatus() },
	onShow() { this.checkLoginStatus() },
	methods: {
		checkLoginStatus() { return },
		toDoctorPage() {
			if (isLoggedIn() && getCurrentUserType() === 'doctor') { uni.reLaunch({ url: '/pages/homeDoctor/homeDoctor' }); return }
			uni.setStorageSync('userType', 'doctor')
			uni.navigateTo({ url: '/pages/login/login?userType=doctor' })
		},
		toPatientPage() {
			if (isLoggedIn() && getCurrentUserType() === 'patient') { uni.reLaunch({ url: '/pages/homePatient/homePatient' }); return }
			uni.setStorageSync('userType', 'patient')
			uni.navigateTo({ url: '/pages/login/login?userType=patient' })
		},
		toFamilyPage() {
			if (isLoggedIn() && getCurrentUserType() === 'family') { uni.reLaunch({ url: '/pages/family/index' }); return }
			uni.setStorageSync('userType', 'family')
			uni.navigateTo({ url: '/pages/login/login?userType=family' })
		}
	}
}
</script>

<style scoped>
.page {
	display: flex;
	flex-direction: column;
}

/* ===== Hero:深空蓝阅片灯箱 ===== */
.hero {
	--ds-scan-h: 230px;
	position: relative;
	padding: 88px 32px 56px;
	background: linear-gradient(160deg, #0C1733 0%, #0A3A8C 55%, #0A5CFF 130%);
}
/* 右上角造影剂青光晕 */
.hero-glow {
	position: absolute;
	top: -60px; right: -60px;
	width: 220px; height: 220px;
	background: radial-gradient(circle, rgba(0,194,215,0.45) 0%, transparent 70%);
	filter: blur(8px);
}
.hero-content {
	position: relative;
	display: flex;
	flex-direction: column;
	align-items: center;
}

/* Logo:旋转神经环 + 医疗十字 + 轨道节点 */
.logo-box {
	position: relative;
	width: 88px; height: 88px;
	border-radius: 24px;
	background: rgba(255,255,255,0.10);
	border: 1px solid rgba(255,255,255,0.18);
	display: flex; align-items: center; justify-content: center;
	margin-bottom: 22px;
	box-shadow: 0 8px 30px rgba(0,194,215,0.25);
}
.logo-ring {
	position: absolute;
	width: 64px; height: 64px;
	border-radius: 50%;
	border: 1.5px dashed rgba(0,194,215,0.6);
	animation: logo-spin 9s linear infinite;
}
@keyframes logo-spin { to { transform: rotate(360deg); } }
.logo-img { position: relative; z-index: 2; width: 58px; height: 58px; border-radius: 16px; }
.logo-dot { position: absolute; width: 6px; height: 6px; border-radius: 50%; background: #00C2D7; box-shadow: 0 0 8px #00C2D7; }
.logo-dot-2 { bottom: 16px; left: 12px; animation: dot-blink 2s ease-in-out infinite; }
.logo-dot-3 { bottom: 20px; right: 18px; animation: dot-blink 2s ease-in-out 0.7s infinite; }
@keyframes dot-blink { 0%,100% { opacity: 1; } 50% { opacity: 0.25; } }

.app-title { font-size: 36px; font-weight: 800; color: #fff; letter-spacing: 2px; margin-bottom: 12px; }
.app-sub-row { display: flex; align-items: center; gap: 10px; }
.sub-line { width: 24px; height: 1px; background: rgba(255,255,255,0.35); }
.app-sub { font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.7); letter-spacing: 1.5px; }

/* ===== Section ===== */
.section-area { padding: 28px 20px 0; }
.section-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 14px; padding: 0 6px; }
.section-label { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); letter-spacing: 0.3px; }
.section-hint { font-size: 11px; font-weight: 600; color: var(--ds-ink-4); letter-spacing: 1px; font-family: var(--ds-font-mono); }

/* ===== Card Group ===== */
.card-group { display: flex; flex-direction: column; gap: 12px; }
.card-item {
	display: flex; align-items: center;
	padding: 18px 18px;
	gap: 16px;
	background: var(--ds-surface);
	border-radius: var(--ds-r-md);
	box-shadow: var(--ds-shadow-sm);
	border: 1px solid var(--ds-hairline);
	transition: transform 0.18s var(--ds-ease), box-shadow 0.18s var(--ds-ease);
}
.item-pressed { transform: scale(0.985); box-shadow: var(--ds-shadow-md); }
.card-icon {
	width: 50px; height: 50px;
	border-radius: 14px;
	display: flex; align-items: center; justify-content: center;
	flex-shrink: 0;
	box-shadow: 0 6px 16px rgba(10,92,255,0.22);
}
.ico { width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; }
.card-body { flex: 1; min-width: 0; }
.card-title { display: block; font-size: 17px; font-weight: 700; color: var(--ds-ink-1); margin-bottom: 3px; }
.card-desc { display: block; font-size: 13px; color: var(--ds-ink-3); }
.card-chevron { flex-shrink: 0; width: 20px; display: flex; align-items: center; justify-content: center; }
.chev { width: 9px; height: 9px; border-top: 2px solid var(--ds-ink-4); border-right: 2px solid var(--ds-ink-4); transform: rotate(45deg); border-radius: 1px; }

/* ===== Footer ===== */
.footer-area { flex: 1; display: flex; align-items: flex-end; justify-content: center; padding: 44px 0 36px; }
.footer-badge { display: flex; align-items: center; gap: 8px; padding: 7px 14px; background: var(--ds-surface); border-radius: var(--ds-r-pill); border: 1px solid var(--ds-hairline); }
.pulse-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--ds-success); box-shadow: 0 0 0 0 rgba(31,184,119,0.5); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(31,184,119,0.5); } 70% { box-shadow: 0 0 0 8px rgba(31,184,119,0); } 100% { box-shadow: 0 0 0 0 rgba(31,184,119,0); } }
.footer-text { font-size: 11px; font-weight: 600; color: var(--ds-ink-3); letter-spacing: 0.8px; }
</style>
