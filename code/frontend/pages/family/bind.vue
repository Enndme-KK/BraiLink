<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack" hover-class="back-pressed">
					<text class="back-char">‹</text>
				</view>
				<text class="nav-title">绑定管理</text>
				<view class="nav-placeholder"></view>
			</view>
		</view>

		<scroll-view scroll-y class="content">
			<!-- 介绍 -->
			<view class="intro-card ds-rise ds-d1">
				<view class="intro-ico">
					<svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="#0A5CFF" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 13a4 4 0 0 0 5.6.5l3-3A4 4 0 0 0 11.9 5l-1.2 1.1"/><path d="M15 11a4 4 0 0 0-5.6-.5l-3 3A4 4 0 0 0 12.1 19l1.2-1.1"/></svg>
				</view>
				<text class="intro-title">管理家属与患者关系</text>
				<text class="intro-desc">使用患者生成的邀请码新增绑定，或解除已有的绑定关系</text>
			</view>

			<!-- 已绑定 -->
			<view class="card ds-rise ds-d2">
				<view class="card-head">
					<view>
						<text class="card-title">已绑定患者</text>
						<text class="card-sub ds-mono">BOUND PATIENTS</text>
					</view>
					<view class="refresh-pill" @click="loadBindings"><text>刷新</text></view>
				</view>

				<view class="loading-line" v-if="loadingBindings">
					<view class="ds-spinner"></view>
					<text>正在加载...</text>
				</view>

				<view class="empty-block" v-else-if="bindings.length === 0">
					<view class="empty-ico">
						<svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#A2A9BC" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg>
					</view>
					<text class="empty-title">暂无绑定患者</text>
					<text class="empty-desc">在下方输入邀请码完成绑定</text>
				</view>

				<view class="binding-item" v-else v-for="binding in bindings" :key="binding.id">
					<view class="patient-avatar"><text>{{ getAvatarText(binding.patient_name) }}</text></view>
					<view class="binding-main">
						<text class="binding-name">{{ binding.patient_name || '已绑定患者' }}</text>
						<text class="binding-meta ds-mono">{{ binding.relationship || '家属' }} · {{ formatDateTime(binding.created_at) }}</text>
					</view>
					<view class="unbind-btn" :class="{ disabled: unbindingId === binding.id }" @click="confirmUnbind(binding)">
						<text>{{ unbindingId === binding.id ? '处理中' : '解绑' }}</text>
					</view>
				</view>
			</view>

			<!-- 新增 -->
			<view class="card ds-rise ds-d3">
				<view class="card-head">
					<view>
						<text class="card-title">新增绑定</text>
						<text class="card-sub ds-mono">INVITE CODE</text>
					</view>
				</view>

				<view class="input-group">
					<text class="input-label">邀请码</text>
					<input class="code-input ds-mono" v-model="inviteCode" type="text" maxlength="10" placeholder="请输入 10 位邀请码" placeholder-class="ph" @input="normalizeInviteCode" />
					<text class="input-hint">仅支持大写字母和数字</text>
				</view>

				<view class="input-group">
					<text class="input-label">与患者关系</text>
					<input class="normal-input" v-model="relationship" type="text" maxlength="20" placeholder="例如：父亲、母亲、配偶、子女" placeholder-class="ph" />
				</view>

				<view class="primary-btn" :class="{ disabled: submitting || inviteCode.length !== 10 }" @click="submitBinding" hover-class="btn-pressed">
					<view class="btn-spinner" v-if="submitting"></view>
					<text class="btn-text" v-else>确认绑定</text>
				</view>
			</view>

			<!-- 说明 -->
			<view class="card ds-rise ds-d4">
				<view class="card-head">
					<view>
						<text class="card-title">绑定说明</text>
						<text class="card-sub ds-mono">HOW IT WORKS</text>
					</view>
				</view>
				<view class="step-list">
					<view class="step-item" v-for="(s, i) in steps" :key="i">
						<view class="step-num ds-mono">0{{ i + 1 }}</view>
						<text class="step-text">{{ s }}</text>
					</view>
				</view>
			</view>
			<view style="height: 24px;"></view>
		</scroll-view>

		<bottom-nav-family current="bind" />
	</view>
</template>

<script>
import { familyAPI } from '@/utils/request.js'
import BottomNavFamily from '@/components/bottom_nav/BottomNavFamily.vue'

export default {
	name: 'FamilyBind',
	components: { BottomNavFamily },
	data() {
		return {
			inviteCode: '', relationship: '',
			submitting: false, loadingBindings: false,
			bindings: [], unbindingId: null,
			steps: [
				'邀请码由患者本人生成，每次生成会替换旧邀请码。',
				'绑定成功后可查看患者基础信息、病历摘要和挂号记录。',
				'解除绑定后，家属端将不再展示该患者的病例和沟通入口。'
			]
		}
	},
	async onLoad() {
		const authModule = await import('@/utils/auth.js')
		if (!authModule.requireAuth()) return
		if (authModule.getCurrentUserType() !== 'family') {
			uni.showToast({ title: '此页面仅限家属访问', icon: 'none' })
			uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' }); return
		}
		this.loadBindings()
	},
	onShow() { this.loadBindings() },
	methods: {
		async loadBindings() {
			this.loadingBindings = true
			try {
				const r = await familyAPI.getMyBindings()
				this.bindings = Array.isArray(r) ? r : []
			} catch (error) {
				uni.showToast({ title: error.response?.data?.error || error.message || '加载绑定关系失败', icon: 'none' })
			} finally { this.loadingBindings = false }
		},
		normalizeInviteCode() {
			const value = (this.inviteCode || '').replace(/[^0-9a-zA-Z]/g, '').toUpperCase()
			this.inviteCode = value.slice(0, 10)
		},
		async submitBinding() {
			this.normalizeInviteCode()
			if (this.inviteCode.length !== 10) { uni.showToast({ title: '请输入 10 位邀请码', icon: 'none' }); return }
			if (this.submitting) return
			this.submitting = true
			try {
				uni.showLoading({ title: '绑定中...', mask: true })
				const r = await familyAPI.bindByInviteCode({ invite_code: this.inviteCode, relationship: this.relationship.trim() })
				uni.hideLoading()
				this.inviteCode = ''; this.relationship = ''
				await this.loadBindings()
				uni.showToast({ title: r.message || '绑定成功', icon: 'success' })
			} catch (error) {
				uni.hideLoading()
				uni.showToast({ title: error.response?.data?.error || error.message || '绑定失败', icon: 'none', duration: 2500 })
			} finally { this.submitting = false }
		},
		confirmUnbind(binding) {
			if (!binding || this.unbindingId) return
			uni.showModal({
				title: '确认解绑', content: `确定解除与"${binding.patient_name || '该患者'}"的绑定关系吗？`,
				confirmText: '解绑', cancelText: '取消',
				success: r => { if (r.confirm) this.unbindPatient(binding) }
			})
		},
		async unbindPatient(binding) {
			this.unbindingId = binding.id
			try {
				uni.showLoading({ title: '解绑中...', mask: true })
				const r = await familyAPI.unbindPatient({ binding_id: binding.id })
				uni.hideLoading()
				await this.loadBindings()
				uni.showToast({ title: r.message || '解绑成功', icon: 'success' })
			} catch (error) {
				uni.hideLoading()
				uni.showToast({ title: error.response?.data?.error || error.message || '解绑失败', icon: 'none' })
			} finally { this.unbindingId = null }
		},
		getAvatarText(name) { return name ? String(name).slice(0, 1) : '患' },
		formatDateTime(value) {
			if (!value) return '—'
			const d = new Date(value); if (isNaN(d.getTime())) return value
			return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
		},
		goBack() {
			const pages = getCurrentPages()
			if (pages.length > 1) uni.navigateBack()
			else uni.reLaunch({ url: '/pages/family/index' })
		}
	}
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: var(--ds-bg); font-family: var(--ds-font); }
.navbar { position: sticky; top: 0; z-index: 100; flex-shrink: 0; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.82); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; display: flex; align-items: center; justify-content: space-between; padding: 52px 16px 12px; }
.nav-back { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
.back-pressed { background: var(--ds-brand-ghost); }
.back-char { font-size: 32px; font-weight: 300; color: var(--ds-brand); line-height: 1; margin-top: -4px; }
.nav-title { font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-placeholder { width: 36px; }

.content { flex: 1; padding: 18px 20px 90px; box-sizing: border-box; }

.intro-card { background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); padding: 26px 20px; text-align: center; margin-bottom: 14px; }
.intro-ico { width: 64px; height: 64px; border-radius: 18px; background: var(--ds-brand-soft); display: flex; align-items: center; justify-content: center; margin: 0 auto 14px; }
.intro-title { display: block; font-size: 18px; font-weight: 800; color: var(--ds-ink-1); margin-bottom: 8px; }
.intro-desc { display: block; font-size: 13px; line-height: 1.65; color: var(--ds-ink-3); }

.card { background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); padding: 18px; margin-bottom: 14px; }
.card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.card-title { display: block; font-size: 16px; font-weight: 800; color: var(--ds-ink-1); }
.card-sub { display: block; margin-top: 4px; font-size: 10px; font-weight: 600; color: var(--ds-ink-4); letter-spacing: 1px; }
.refresh-pill { padding: 6px 12px; border-radius: var(--ds-r-pill); background: var(--ds-brand-soft); }
.refresh-pill text { font-size: 12px; font-weight: 600; color: var(--ds-brand); }

.loading-line { display: flex; align-items: center; gap: 10px; padding: 16px 0; color: var(--ds-ink-3); font-size: 13px; }

.empty-block { padding: 24px 14px; text-align: center; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); }
.empty-ico { width: 52px; height: 52px; border-radius: 50%; background: var(--ds-surface); display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; }
.empty-title { display: block; font-size: 14px; font-weight: 700; color: var(--ds-ink-2); margin-bottom: 4px; }
.empty-desc { display: block; font-size: 12px; color: var(--ds-ink-4); }

.binding-item { display: flex; align-items: center; gap: 12px; padding: 13px 0; border-top: 1px solid var(--ds-hairline); }
.binding-item:first-of-type { border-top: none; }
.patient-avatar { width: 44px; height: 44px; border-radius: 14px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; flex-shrink: 0;  }
.patient-avatar text { color: #fff; font-size: 18px; font-weight: 800; }
.binding-main { flex: 1; min-width: 0; }
.binding-name { display: block; font-size: 15px; font-weight: 700; color: var(--ds-ink-1); margin-bottom: 4px; }
.binding-meta { display: block; font-size: 11px; color: var(--ds-ink-3); letter-spacing: 0.3px; }
.unbind-btn { padding: 7px 13px; border-radius: var(--ds-r-pill); background: rgba(255,77,94,0.13); flex-shrink: 0; }
.unbind-btn text { font-size: 12px; font-weight: 700; color: var(--ds-danger); }
.unbind-btn.disabled { opacity: 0.55; }

.input-group { margin-bottom: 16px; }
.input-label { display: block; font-size: 13px; font-weight: 600; color: var(--ds-ink-2); margin-bottom: 8px; }
.code-input { width: 100%; height: 50px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 0 14px; box-sizing: border-box; font-size: 18px; font-weight: 800; letter-spacing: 4px; text-align: center; color: var(--ds-ink-1); border: 1px solid var(--ds-hairline); }
.normal-input { width: 100%; height: 48px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 0 14px; box-sizing: border-box; font-size: 14px; color: var(--ds-ink-1); border: 1px solid var(--ds-hairline); }
.ph { color: var(--ds-ink-4); }
.input-hint { display: block; margin-top: 8px; font-size: 11px; color: var(--ds-ink-4); }

.primary-btn { height: 48px; border-radius: var(--ds-r-sm); background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); display: flex; align-items: center; justify-content: center; transition: transform 0.18s; }
.primary-btn:active, .btn-pressed { transform: scale(0.97); }
.primary-btn.disabled { opacity: 0.55; pointer-events: none; }
.btn-text { font-size: 16px; font-weight: 600; color: #fff; letter-spacing: 0.5px; }
.btn-spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.35); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.step-list { display: flex; flex-direction: column; gap: 10px; }
.step-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 14px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); }
.step-num { font-size: 14px; font-weight: 800; color: var(--ds-brand); flex-shrink: 0; }
.step-text { flex: 1; font-size: 13px; line-height: 1.6; color: var(--ds-ink-2); }
</style>
