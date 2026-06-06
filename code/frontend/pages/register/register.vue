<template>
	<view class="page">
		<!-- 导航栏 -->
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack" hover-class="back-pressed">
					<text class="back-char">‹</text>
				</view>
				<text class="nav-title">{{ userTypeText }}</text>
				<view class="nav-placeholder"></view>
			</view>
		</view>

		<view class="content">
			<!-- 品牌头部 -->
			<view class="brand-area ds-rise ds-d1">
				<view class="brand-logo ds-scanline">
					<image class="brand-img" src="/static/logo.png" mode="aspectFit"></image>
				</view>
				<text class="brand-name">BraiLink</text>
				<view class="brand-sub-row">
					<view class="sub-line"></view>
					<text class="brand-sub ds-mono">CREATE ACCOUNT</text>
					<view class="sub-line"></view>
				</view>
			</view>

			<!-- 标题 -->
			<view class="title-area ds-rise ds-d2">
				<text class="page-title">创建账号</text>
				<text class="page-sub">完成{{ userTypeText }}注册</text>
			</view>

			<!-- 表单 -->
			<view class="form-card ds-rise ds-d3">
				<!-- 用户名 -->
				<view class="field-item">
					<view class="field-ico">
						<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
					</view>
					<input class="field-input" type="text" placeholder="用户名 (3-20 字符)" v-model="formData.username" maxlength="20" />
				</view>
				<view class="field-divider"></view>

				<!-- 邮箱 -->
				<view class="field-item">
					<view class="field-ico">
						<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>
					</view>
					<input class="field-input" type="text" placeholder="邮箱地址" v-model="formData.email" />
				</view>
				<view class="field-divider"></view>

				<!-- 真实姓名 -->
				<view class="field-item">
					<view class="field-ico">
						<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16l-3-2-2 2-2-2-2 2-2-2-3 2z"/><path d="M9 7h6M9 11h6M9 15h4"/></svg>
					</view>
					<input class="field-input" type="text" placeholder="真实姓名" v-model="formData.name" maxlength="50" />
				</view>
				<view class="field-divider"></view>

				<!-- 手机号 -->
				<view class="field-item">
					<view class="field-ico">
						<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18.5h2"/></svg>
					</view>
					<input class="field-input" type="number" placeholder="手机号" v-model="formData.phone" maxlength="11" />
				</view>
				<view class="field-divider"></view>

				<!-- 密码 -->
				<view class="field-item">
					<view class="field-ico">
						<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
					</view>
					<input class="field-input" :type="passwordVisible ? 'text' : 'password'" placeholder="密码 (至少 6 位)" v-model="formData.password" maxlength="20" />
					<view class="field-action" @click="togglePassword">
						<text class="action-text">{{ passwordVisible ? '隐藏' : '显示' }}</text>
					</view>
				</view>
				<view class="field-divider"></view>

				<!-- 确认密码 -->
				<view class="field-item">
					<view class="field-ico">
						<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
					</view>
					<input class="field-input" :type="confirmPasswordVisible ? 'text' : 'password'" placeholder="再次输入密码" v-model="formData.confirmPassword" maxlength="20" />
					<view class="field-action" @click="toggleConfirmPassword">
						<text class="action-text">{{ confirmPasswordVisible ? '隐藏' : '显示' }}</text>
					</view>
				</view>
			</view>

			<!-- 字段提示 (软提醒) -->
			<view class="hint-area" v-if="liveHint">
				<view class="hint-dot"></view>
				<text class="hint-text">{{ liveHint }}</text>
			</view>

			<!-- 错误提示 -->
			<view class="error-area" v-if="errorMsg">
				<text class="error-text">{{ errorMsg }}</text>
			</view>

			<!-- 注册按钮 -->
			<view class="btn-area ds-rise ds-d4">
				<view class="primary-btn" :class="{ disabled: isLoading }" @click="handleRegister" hover-class="btn-pressed">
					<view class="btn-spinner" v-if="isLoading"></view>
					<text class="btn-text" v-else>注册</text>
				</view>
			</view>

			<!-- 登录链接 -->
			<view class="link-area ds-rise ds-d5">
				<text class="link-dim">已有账号？</text>
				<text class="link-blue" @click="goToLogin">立即登录</text>
			</view>
		</view>
	</view>
</template>

<script>
import { authAPI } from '@/utils/request.js'

export default {
	data() {
		return {
			userType: '',
			formData: {
				username: '', email: '', name: '', phone: '',
				password: '', confirmPassword: ''
			},
			passwordVisible: false,
			confirmPasswordVisible: false,
			isLoading: false,
			errorMsg: ''
		}
	},
	computed: {
		userTypeText() {
			if (this.userType === 'doctor') return '医生端注册'
			if (this.userType === 'family') return '家属端注册'
			return '患者端注册'
		},
		isValidEmail() {
			const r = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
			return !this.formData.email || r.test(this.formData.email)
		},
		liveHint() {
			const f = this.formData
			if (f.username && f.username.length < 3) return '用户名至少 3 个字符'
			if (f.email && !this.isValidEmail) return '邮箱格式不正确'
			if (f.phone && f.phone.length !== 11) return '请输入 11 位手机号'
			if (f.password && f.password.length < 6) return '密码至少 6 位'
			if (f.confirmPassword && f.password !== f.confirmPassword) return '两次密码不一致'
			return ''
		}
	},
	onLoad(options) {
		this.userType = options.userType || 'patient'
	},
	methods: {
		togglePassword() { this.passwordVisible = !this.passwordVisible },
		toggleConfirmPassword() { this.confirmPasswordVisible = !this.confirmPasswordVisible },
		validateForm() {
			const f = this.formData
			if (!f.username.trim()) { this.errorMsg = '请输入用户名'; return false }
			if (f.username.trim().length < 3) { this.errorMsg = '用户名至少 3 个字符'; return false }
			if (!f.email.trim()) { this.errorMsg = '请输入邮箱地址'; return false }
			if (!this.isValidEmail) { this.errorMsg = '邮箱格式不正确'; return false }
			if (f.phone && f.phone.length !== 11) { this.errorMsg = '请输入 11 位手机号'; return false }
			if (!f.password) { this.errorMsg = '请输入密码'; return false }
			if (f.password.length < 6) { this.errorMsg = '密码至少 6 位'; return false }
			if (!f.confirmPassword) { this.errorMsg = '请再次输入密码'; return false }
			if (f.password !== f.confirmPassword) { this.errorMsg = '两次密码不一致'; return false }
			this.errorMsg = ''; return true
		},
		async handleRegister() {
			if (!this.validateForm() || this.isLoading) return
			this.isLoading = true; this.errorMsg = ''
			try {
				uni.showLoading({ title: '注册中...', mask: true })
				const f = this.formData
				const payload = {
					username: f.username.trim(),
					email: f.email.trim(),
					password: f.password,
					password_confirm: f.confirmPassword,
					user_type: this.userType
				}
				if (f.name.trim()) payload.name = f.name.trim()
				if (f.phone.trim()) payload.phone = f.phone.trim()

				const response = await authAPI.register(payload)
				uni.hideLoading(); this.isLoading = false

				if (response && response.token && response.user) {
					const { saveLoginInfo } = await import('@/utils/auth.js')
					saveLoginInfo(response.token, response.user)
					uni.showToast({ title: '注册成功', icon: 'success', duration: 1500 })

					const target =
						response.user.user_type === 'doctor' ? '/pages/completeProfile/completeProfile?userType=doctor&isNew=true' :
						response.user.user_type === 'patient' ? '/pages/completeProfile/completeProfile?userType=patient&isNew=true' :
						response.user.user_type === 'family' ? '/pages/family/index' :
						'/pages/homePatient/homePatient'

					setTimeout(() => {
						uni.reLaunch({
							url: target,
							fail: (err) => {
								console.error('[register] reLaunch 失败:', err)
								uni.showToast({ title: '页面跳转失败', icon: 'none', duration: 3000 })
							}
						})
					}, 1200)
				} else {
					uni.showToast({ title: '注册成功，请登录', icon: 'success', duration: 1500 })
					setTimeout(() => uni.navigateBack({ delta: 1 }), 1200)
				}
			} catch (error) {
				uni.hideLoading(); this.isLoading = false
				console.error('[register] 注册失败:', error)
				let message = ''
				const data = error && error.response && error.response.data
				if (data && typeof data === 'object') {
					const fields = ['username','email','password','password1','password2','password_confirm','re_password','user_type','phone','name','detail','message','non_field_errors']
					for (const k of fields) {
						if (data[k]) {
							const v = Array.isArray(data[k]) ? data[k][0] : data[k]
							message = typeof v === 'string' ? v : JSON.stringify(v)
							break
						}
					}
					if (!message) {
						const k0 = Object.keys(data)[0]
						if (k0) {
							const v = Array.isArray(data[k0]) ? data[k0][0] : data[k0]
							message = typeof v === 'string' ? v : JSON.stringify(v)
						}
					}
				}
				if (!message) message = (error && error.message) || '注册失败，请稍后重试'
				this.errorMsg = message
				uni.showToast({ title: message, icon: 'none', duration: 3000 })
			}
		},
		goToLogin() { uni.navigateBack({ delta: 1 }) },
		goBack() { uni.navigateBack({ delta: 1 }) }
	}
}
</script>

<style scoped>
.page {
	min-height: 100vh;
	background: var(--ds-bg);
	display: flex;
	flex-direction: column;
	font-family: var(--ds-font);
}

/* 导航栏 */
.navbar { position: sticky; top: 0; z-index: 100; }
.navbar-bg {
	position: absolute; top: 0; left: 0; right: 0; bottom: 0;
	background: rgba(244,246,251,0.82);
	backdrop-filter: saturate(180%) blur(20px);
	-webkit-backdrop-filter: saturate(180%) blur(20px);
	border-bottom: 1px solid var(--ds-hairline);
}
.navbar-inner {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 52px 16px 12px;
}
.nav-back {
	width: 36px; height: 36px;
	display: flex; align-items: center; justify-content: center;
	border-radius: 12px;
	transition: background 0.18s var(--ds-ease);
}
.back-pressed { background: var(--ds-brand-ghost); }
.back-char { font-size: 32px; font-weight: 300; color: var(--ds-brand); line-height: 1; margin-top: -4px; }
.nav-title { font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-placeholder { width: 36px; }

.content { flex: 1; padding-bottom: 36px; }

/* 品牌头部 */
.brand-area { display: flex; flex-direction: column; align-items: center; padding: 18px 20px 4px; }
.brand-logo {
	--ds-scan-h: 76px;
	width: 76px; height: 76px;
	border-radius: 22px;
	background: var(--ds-surface);
	box-shadow: var(--ds-shadow-md);
	display: flex; align-items: center; justify-content: center;
	overflow: hidden;
	margin-bottom: 12px;
}
.brand-img { width: 76px; height: 76px; }
.brand-name { font-size: 22px; font-weight: 800; color: var(--ds-ink-1); letter-spacing: 2px; margin-bottom: 8px; }
.brand-sub-row { display: flex; align-items: center; gap: 8px; }
.sub-line { width: 18px; height: 1px; background: var(--ds-ink-4); }
.brand-sub { font-size: 10px; font-weight: 600; color: var(--ds-ink-3); letter-spacing: 1.5px; }

/* 标题 */
.title-area { padding: 14px 20px 18px; }
.page-title { display: block; font-size: 28px; font-weight: 800; color: var(--ds-ink-1); letter-spacing: -0.5px; margin-bottom: 6px; }
.page-sub { display: block; font-size: 15px; color: var(--ds-ink-3); }

/* 表单 */
.form-card {
	margin: 0 20px;
	background: var(--ds-surface);
	border-radius: var(--ds-r-md);
	overflow: hidden;
	box-shadow: var(--ds-shadow-sm);
	border: 1px solid var(--ds-hairline);
}
.field-item { display: flex; align-items: center; padding: 0 16px; min-height: 54px; gap: 12px; }
.field-ico { width: 24px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.field-input {
	flex: 1;
	font-size: 15px;
	color: var(--ds-ink-1);
	background: transparent;
	border: none;
	height: 54px;
}
.field-input::placeholder { color: var(--ds-ink-4); }
.field-divider { height: 1px; background: var(--ds-hairline); margin-left: 52px; }
.field-action { padding: 8px 0 8px 12px; flex-shrink: 0; }
.action-text { font-size: 14px; font-weight: 600; color: var(--ds-brand); }

/* 软提醒 */
.hint-area { display: flex; align-items: center; gap: 8px; padding: 10px 24px 0; }
.hint-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--ds-warning); }
.hint-text { font-size: 12px; color: var(--ds-ink-3); }

/* 错误 */
.error-area { padding: 12px 24px 0; }
.error-text { font-size: 13px; color: var(--ds-danger); }

/* 按钮 */
.btn-area { padding: 22px 20px 0; }
.primary-btn {
	height: 52px;
	border-radius: var(--ds-r-sm);
	background: var(--ds-grad-brand);
	box-shadow: var(--ds-shadow-brand);
	display: flex; align-items: center; justify-content: center;
	transition: transform 0.18s var(--ds-ease), box-shadow 0.18s var(--ds-ease), opacity 0.18s;
}
.primary-btn:active, .btn-pressed { transform: scale(0.97);  }
.primary-btn.disabled { opacity: 0.5; pointer-events: none; }
.btn-text { font-size: 17px; font-weight: 600; color: #fff; letter-spacing: 1px; }
.btn-spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }

/* 链接 */
.link-area { display: flex; justify-content: center; align-items: center; gap: 4px; padding: 16px; }
.link-dim { font-size: 14px; color: var(--ds-ink-3); }
.link-blue { font-size: 14px; font-weight: 600; color: var(--ds-brand); }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
