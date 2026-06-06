<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack" hover-class="back-pressed">
					<text class="back-char">‹</text>
				</view>
				<text class="nav-title">邀请家属</text>
				<view class="nav-action" :class="{ disabled: loading }" @click="generateInviteCode">
					<text class="action-text">{{ loading ? '生成中' : (inviteCode ? '重生成' : '生成') }}</text>
				</view>
			</view>
		</view>

		<view class="content">
			<!-- 介绍 -->
			<view class="intro-card ds-rise ds-d1">
				<view class="intro-ico">
					<svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="#0A5CFF" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 13a4 4 0 0 0 5.6.5l3-3A4 4 0 0 0 11.9 5l-1.2 1.1"/><path d="M15 11a4 4 0 0 0-5.6-.5l-3 3A4 4 0 0 0 12.1 19l1.2-1.1"/></svg>
				</view>
				<text class="intro-title">生成一次性邀请码</text>
				<text class="intro-desc">把邀请码发给家属账号，对方在家属端输入后即可完成绑定。每次重新生成会替换旧邀请码。</text>
			</view>

			<!-- 邀请码卡 -->
			<view class="card ds-rise ds-d2">
				<view class="card-head">
					<view>
						<text class="card-title">当前邀请码</text>
						<text class="card-sub ds-mono">{{ generatedAt ? `GENERATED ${generatedAt}` : 'GENERATE TO START' }}</text>
					</view>
					<view class="status-pill" :class="{ active: inviteCode }">
						<view class="status-dot" :class="{ active: inviteCode }"></view>
						<text>{{ inviteCode ? '可使用' : '未生成' }}</text>
					</view>
				</view>

				<view class="code-box ds-scanline" :class="{ empty: !inviteCode }">
					<text class="invite-code ds-mono">{{ inviteCode || '— — — — —' }}</text>
				</view>

				<view class="button-row">
					<view class="primary-btn" :class="{ disabled: loading }" @click="generateInviteCode" hover-class="btn-pressed">
						<text class="btn-text">{{ loading ? '生成中...' : (inviteCode ? '重新生成' : '生成邀请码') }}</text>
					</view>
					<view class="secondary-btn" :class="{ disabled: !inviteCode }" @click="copyInviteCode" hover-class="btn-pressed">
						<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#0A5CFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
						<text class="btn-secondary-text">复制</text>
					</view>
				</view>
			</view>

			<!-- 步骤 -->
			<view class="card ds-rise ds-d3">
				<view class="card-head">
					<view>
						<text class="card-title">绑定流程</text>
						<text class="card-sub ds-mono">PATIENT TO FAMILY</text>
					</view>
				</view>
				<view class="step-list">
					<view class="step-item" v-for="(s, i) in steps" :key="i">
						<view class="step-num ds-mono">0{{ i + 1 }}</view>
						<text class="step-text">{{ s }}</text>
					</view>
				</view>
			</view>
			<view style="height: 90px;"></view>
		</view>

		<bottom-nav-patient current="profile" />
	</view>
</template>

<script>
import { patientAPI } from '@/utils/request.js'
import BottomNavPatient from '@/components/bottom_nav/BottomNavPatient.vue'

export default {
	name: 'PatientBindFamily',
	components: { BottomNavPatient },
	data() {
		return {
			inviteCode: '', generatedAt: '', loading: false,
			steps: [
				'患者点击右上角"生成"按钮，得到 10 位邀请码。',
				'家属登录家属端，在"绑定"页面输入邀请码和关系。',
				'绑定成功后，家属可查看患者摘要并联系相关医生。'
			]
		}
	},
	async onLoad() {
		const authModule = await import('@/utils/auth.js')
		if (!authModule.requireAuth()) return
		if (authModule.getCurrentUserType() !== 'patient') {
			uni.showToast({ title: '此页面仅限患者访问', icon: 'none' })
			uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' })
		}
	},
	methods: {
		formatDateTime(s) {
			if (!s) return ''
			const d = new Date(s); const p = n => String(n).padStart(2, '0')
			return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
		},
		async generateInviteCode() {
			if (this.loading) return
			this.loading = true
			try {
				uni.showLoading({ title: '生成中...', mask: true })
				const r = await patientAPI.generateFamilyInviteCode()
				const invite = r.invite || {}
				this.inviteCode = invite.code || ''
				this.generatedAt = this.formatDateTime(invite.created_at)
				uni.hideLoading()
				uni.showToast({ title: r.message || '邀请码已生成', icon: 'success' })
			} catch (e) {
				uni.hideLoading()
				uni.showToast({ title: e.response?.data?.error || e.message || '生成失败', icon: 'none', duration: 2500 })
			} finally { this.loading = false }
		},
		copyInviteCode() {
			if (!this.inviteCode) { uni.showToast({ title: '请先生成邀请码', icon: 'none' }); return }
			uni.setClipboardData({ data: this.inviteCode, success: () => uni.showToast({ title: '邀请码已复制', icon: 'success' }) })
		},
		goBack() {
			const pages = getCurrentPages()
			if (pages.length > 1) uni.navigateBack()
			else uni.navigateTo({ url: '/pages/personalCenterPatient/personalCenterPatient' })
		}
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); font-family: var(--ds-font); padding-bottom: 90px; }
.navbar { position: sticky; top: 0; z-index: 100; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.82); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; display: flex; align-items: center; justify-content: space-between; padding: 52px 16px 12px; }
.nav-back { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
.back-pressed { background: var(--ds-brand-ghost); }
.back-char { font-size: 32px; font-weight: 300; color: var(--ds-brand); line-height: 1; margin-top: -4px; }
.nav-title { font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-action { padding: 6px 14px; border-radius: var(--ds-r-pill); background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); }
.nav-action.disabled { opacity: 0.55; pointer-events: none; }
.action-text { font-size: 13px; font-weight: 600; color: #fff; }

.content { padding: 18px 20px 0; }

.intro-card { background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); padding: 26px 20px; text-align: center; margin-bottom: 14px; }
.intro-ico { width: 64px; height: 64px; border-radius: 18px; background: var(--ds-brand-soft); display: flex; align-items: center; justify-content: center; margin: 0 auto 14px; }
.intro-title { display: block; font-size: 18px; font-weight: 800; color: var(--ds-ink-1); margin-bottom: 8px; }
.intro-desc { display: block; font-size: 13px; line-height: 1.65; color: var(--ds-ink-3); }

.card { background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); padding: 18px; margin-bottom: 14px; }
.card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.card-title { display: block; font-size: 16px; font-weight: 800; color: var(--ds-ink-1); }
.card-sub { display: block; margin-top: 4px; font-size: 10px; font-weight: 600; color: var(--ds-ink-4); letter-spacing: 1px; }

.status-pill { display: flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: var(--ds-r-pill); background: var(--ds-bg-sunken); flex-shrink: 0; }
.status-pill.active { background: rgba(31,184,119,0.13); }
.status-pill text { font-size: 11px; font-weight: 700; color: var(--ds-ink-3); }
.status-pill.active text { color: var(--ds-success); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--ds-ink-4); }
.status-dot.active { background: var(--ds-success); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(31,184,119,0.5); } 70% { box-shadow: 0 0 0 6px rgba(31,184,119,0); } 100% { box-shadow: 0 0 0 0 rgba(31,184,119,0); } }

.code-box { --ds-scan-h: 110px; min-height: 110px; border-radius: var(--ds-r-sm); background: linear-gradient(160deg, #0C1733 0%, #0A3A8C 55%, #0A5CFF 130%); border: 1px dashed rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; padding: 14px; box-sizing: border-box; overflow: hidden; position: relative; }
.code-box.empty { background: var(--ds-bg-sunken); border-color: var(--ds-hairline); }
.invite-code { font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #fff; text-align: center; word-break: break-all; }
.code-box.empty .invite-code { font-size: 22px; letter-spacing: 4px; color: var(--ds-ink-4); }

.button-row { display: flex; gap: 10px; margin-top: 16px; }
.primary-btn { flex: 1; height: 46px; border-radius: var(--ds-r-sm); background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); display: flex; align-items: center; justify-content: center; transition: transform 0.18s; }
.primary-btn:active, .btn-pressed { transform: scale(0.97); }
.primary-btn.disabled { opacity: 0.55; pointer-events: none; }
.btn-text { font-size: 15px; font-weight: 600; color: #fff; }
.secondary-btn { flex: 1; height: 46px; border-radius: var(--ds-r-sm); background: var(--ds-brand-soft); display: flex; align-items: center; justify-content: center; gap: 8px; }
.secondary-btn.disabled { opacity: 0.55; pointer-events: none; }
.btn-secondary-text { font-size: 15px; font-weight: 600; color: var(--ds-brand); }

.step-list { display: flex; flex-direction: column; gap: 10px; }
.step-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 14px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); }
.step-num { font-size: 14px; font-weight: 800; color: var(--ds-brand); flex-shrink: 0; }
.step-text { flex: 1; font-size: 13px; line-height: 1.6; color: var(--ds-ink-2); }
</style>
