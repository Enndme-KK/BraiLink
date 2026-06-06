<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack" hover-class="back-pressed">
					<text class="back-char">‹</text>
				</view>
				<text class="nav-title">修改密码</text>
				<view class="nav-placeholder"></view>
			</view>
		</view>

		<view class="content">
			<view class="card ds-rise ds-d1">
				<view class="field-item">
					<view class="field-ico">
						<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
					</view>
					<input class="field-input" :type="showOld ? 'text' : 'password'" placeholder="请输入原密码" v-model="pri_password" maxlength="20" />
					<view class="field-action" @click="showOld = !showOld"><text class="action-text">{{ showOld ? '隐藏' : '显示' }}</text></view>
				</view>
				<view class="field-divider"></view>
				<view class="field-item">
					<view class="field-ico">
						<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
					</view>
					<input class="field-input" :type="showNew ? 'text' : 'password'" placeholder="请输入新密码" v-model="new_password" maxlength="20" />
					<view class="field-action" @click="showNew = !showNew"><text class="action-text">{{ showNew ? '隐藏' : '显示' }}</text></view>
				</view>
				<view class="field-divider"></view>
				<view class="field-item">
					<view class="field-ico">
						<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
					</view>
					<input class="field-input" :type="showNew2 ? 'text' : 'password'" placeholder="再次输入新密码" v-model="new_password2" maxlength="20" />
					<view class="field-action" @click="showNew2 = !showNew2"><text class="action-text">{{ showNew2 ? '隐藏' : '显示' }}</text></view>
				</view>
			</view>

			<view class="hint-area ds-rise ds-d2">
				<view class="hint-dot"></view>
				<text class="hint-text">密码为 6-18 位，可由字母、数字或字母加数字组合</text>
			</view>

			<view class="btn-area ds-rise ds-d3">
				<view class="primary-btn" @click="finish" hover-class="btn-pressed">
					<text class="btn-text">确认修改</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			pri_password: '', new_password: '', new_password2: '',
			showOld: false, showNew: false, showNew2: false,
			submitting: false
		}
	},
	methods: {
		goBack() { uni.navigateBack({ delta: 1 }) },
		async finish() {
			if (this.submitting) return
			if (!this.pri_password) return uni.showToast({ title: '请输入原密码', icon: 'none' })
			if (!this.new_password || this.new_password.length < 6) return uni.showToast({ title: '新密码至少 6 位', icon: 'none' })
			if (this.new_password !== this.new_password2) return uni.showToast({ title: '两次密码不一致', icon: 'none' })
			this.submitting = true
			try {
				uni.showLoading({ title: '修改中...', mask: true })
				const { authAPI } = await import('@/utils/request.js')
				const resp = await authAPI.changePassword({
					old_password: this.pri_password,
					new_password: this.new_password
				})
				// 后端会签发新 token，本地同步保存
				if (resp && resp.token) {
					try { uni.setStorageSync('token', resp.token) } catch (e) {}
				}
				uni.hideLoading()
				uni.showToast({ title: '密码修改成功', icon: 'success', duration: 1500 })
				setTimeout(() => uni.navigateBack({ delta: 1 }), 1200)
			} catch (e) {
				uni.hideLoading()
				const msg = (e && e.response && e.response.data && e.response.data.error) || e.message || '修改失败'
				uni.showToast({ title: msg, icon: 'none', duration: 2500 })
			} finally {
				this.submitting = false
			}
		}
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); font-family: var(--ds-font); }
.navbar { position: sticky; top: 0; z-index: 100; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.82); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; display: flex; align-items: center; justify-content: space-between; padding: 52px 16px 12px; }
.nav-back { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; transition: background 0.18s; }
.back-pressed { background: var(--ds-brand-ghost); }
.back-char { font-size: 32px; font-weight: 300; color: var(--ds-brand); line-height: 1; margin-top: -4px; }
.nav-title { font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-placeholder { width: 36px; }

.content { padding: 18px 20px 0; }
.card { background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); overflow: hidden; }
.field-item { display: flex; align-items: center; padding: 0 16px; min-height: 54px; gap: 12px; }
.field-ico { width: 24px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.field-input { flex: 1; font-size: 15px; color: var(--ds-ink-1); background: transparent; border: none; height: 54px; }
.field-divider { height: 1px; background: var(--ds-hairline); margin-left: 52px; }
.field-action { padding: 8px 0 8px 12px; }
.action-text { font-size: 14px; font-weight: 600; color: var(--ds-brand); }

.hint-area { display: flex; align-items: center; gap: 8px; padding: 10px 24px 0; }
.hint-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--ds-warning); }
.hint-text { font-size: 12px; color: var(--ds-ink-3); }

.btn-area { padding: 24px 0 0; }
.primary-btn { height: 52px; border-radius: var(--ds-r-sm); background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); display: flex; align-items: center; justify-content: center; transition: transform 0.18s; }
.primary-btn:active, .btn-pressed { transform: scale(0.97); }
.btn-text { font-size: 17px; font-weight: 600; color: #fff; letter-spacing: 1px; }
</style>
