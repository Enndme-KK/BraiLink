<template>
	<view class="page">
		<!-- 导航栏 -->
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack">
					<text class="back-char">‹</text>
				</view>
				<text class="nav-title">{{ userTypeText }}</text>
				<view class="nav-placeholder"></view>
			</view>
		</view>

		<view class="content">
				<!-- 品牌头部:图标 + BraiLink -->
				<view class="brand-area ds-rise ds-d1">
					<view class="brand-logo ds-scanline">
						<image class="brand-img" src="/static/logo.png" mode="aspectFit"></image>
					</view>
					<text class="brand-name">BraiLink</text>
					<view class="brand-sub-row">
						<view class="sub-line"></view>
						<text class="brand-sub ds-mono">AI DIAGNOSIS</text>
						<view class="sub-line"></view>
					</view>
				</view>

				<!-- 标题 -->
				<view class="title-area ds-rise ds-d2">
					<text class="page-title">欢迎回来</text>
					<text class="page-sub">登录您的{{ userTypeText }}账号</text>
				</view>

				<!-- 表单 -->
				<view class="form-card ds-rise ds-d3">
					<view class="field-item">
						<view class="field-ico">
							<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
						</view>
						<input class="field-input" type="text" placeholder="请输入用户名" v-model="formData.username" maxlength="20" />
					</view>
					<view class="field-divider"></view>
					<view class="field-item">
						<view class="field-ico">
							<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#69728C" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
						</view>
						<input class="field-input" :type="passwordVisible ? 'text' : 'password'" placeholder="请输入密码" v-model="formData.password" maxlength="20" />
						<view class="field-action" @click="togglePassword">
							<text class="action-text">{{ passwordVisible ? '隐藏' : '显示' }}</text>
						</view>
					</view>
				</view>

				<!-- 错误 -->
				<view class="error-area" v-if="errorMsg">
					<text class="error-text">{{ errorMsg }}</text>
				</view>

				<!-- 登录按钮 -->
				<view class="btn-area ds-rise ds-d4">
					<view class="primary-btn" :class="{ disabled: isLoading }" @click="handleLogin" hover-class="btn-pressed">
						<view class="btn-spinner" v-if="isLoading"></view>
						<text class="btn-text" v-else>登录</text>
					</view>
				</view>

				<!-- 注册链接 -->
				<view class="link-area ds-rise ds-d5">
					<text class="link-dim">还没有账号？</text>
					<text class="link-blue" @click="goToRegister">立即注册</text>
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
			formData: { username: '', password: '' },
			passwordVisible: false,
			isLoading: false,
			errorMsg: ''
		}
	},
	computed: {
		userTypeText() {
			if (this.userType === 'doctor') return '医生端登录'
			if (this.userType === 'family') return '家属端登录'
			return '患者端登录'
		}
	},
	onLoad(options) {
		this.userType = options.userType || uni.getStorageSync('userType') || 'patient'
		uni.setStorageSync('userType', this.userType)
	},
	methods: {
		togglePassword() { this.passwordVisible = !this.passwordVisible },
		validateForm() {
			if (!this.formData.username.trim()) { this.errorMsg = '请输入用户名'; return false }
			if (!this.formData.password) { this.errorMsg = '请输入密码'; return false }
			if (this.formData.password.length < 6) { this.errorMsg = '密码长度不能少于6位'; return false }
			this.errorMsg = ''; return true
		},
		async handleLogin() {
			if (!this.validateForm() || this.isLoading) return
			this.isLoading = true; this.errorMsg = ''
			try {
				uni.showLoading({ title: '登录中...', mask: true })
				const response = await authAPI.login({ username: this.formData.username.trim(), password: this.formData.password })
				uni.hideLoading()
				this.isLoading = false

				if (!response || !response.user || !response.token) {
					this.errorMsg = '登录响应异常，请重试'
					uni.showToast({ title: this.errorMsg, icon: 'none', duration: 2000 })
					return
				}
				if (response.user.user_type !== this.userType) {
					const m = { doctor: '医生', patient: '患者', family: '家属' }
					this.errorMsg = `该账号为${m[response.user.user_type] || '其他'}账号，请切换身份登录`
					return
				}
				const { saveLoginInfo } = await import('@/utils/auth.js')
				saveLoginInfo(response.token, response.user)
				uni.showToast({ title: '登录成功', icon: 'success', duration: 1500 })
				const targetUrl = response.user.user_type === 'family'
					? '/pages/family/index'
					: response.user.user_type === 'doctor'
						? '/pages/homeDoctor/homeDoctor'
						: '/pages/homePatient/homePatient'
				setTimeout(() => {
					uni.reLaunch({
						url: targetUrl,
						fail: (err) => {
							console.error('[login] reLaunch 失败:', err)
							uni.showToast({ title: '页面跳转失败: ' + (err && err.errMsg || ''), icon: 'none', duration: 3000 })
						}
					})
				}, 1200)
			} catch (error) {
				uni.hideLoading(); this.isLoading = false
				console.error('[login] 登录失败:', error)
				let msg = '登录失败，请检查用户名和密码'
				if (error) {
					const data = error.response && error.response.data
					if (data && typeof data === 'object') {
						if (data.non_field_errors) msg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors
						else if (data.detail) msg = data.detail
						else if (data.message) msg = data.message
					} else if (error.message) {
						msg = error.message
					}
					if (msg.includes('无法连接到服务器') || msg.includes('connect')) msg = '无法连接到后端服务器，请检查后端是否已启动'
				}
				this.errorMsg = msg
				uni.showToast({ title: msg, icon: 'none', duration: 3000 })
			}
		},
		goToRegister() { uni.navigateTo({ url: `/pages/register/register?userType=${this.userType}` }) },
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
.navbar {
	position: sticky;
	top: 0;
	z-index: 100;
}
.navbar-bg {
	position: absolute;
	top: 0; left: 0; right: 0; bottom: 0;
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
.nav-back { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; }
.back-char { font-size: 32px; font-weight: 300; color: var(--ds-brand); line-height: 1; }
.nav-title { font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-placeholder { width: 36px; }

.content { flex: 1; }

/* 品牌头部 */
.brand-area { display: flex; flex-direction: column; align-items: center; padding: 24px 20px 8px; }
.brand-logo {
	--ds-scan-h: 84px;
	width: 84px; height: 84px;
	border-radius: 22px;
	background: var(--ds-surface);
	box-shadow: var(--ds-shadow-md);
	display: flex; align-items: center; justify-content: center;
	overflow: hidden;
	margin-bottom: 14px;
}
.brand-img { width: 84px; height: 84px; }
.brand-name { font-size: 24px; font-weight: 800; color: var(--ds-ink-1); letter-spacing: 2px; margin-bottom: 8px; }
.brand-sub-row { display: flex; align-items: center; gap: 8px; }
.sub-line { width: 18px; height: 1px; background: var(--ds-ink-4); }
.brand-sub { font-size: 10px; font-weight: 600; color: var(--ds-ink-3); letter-spacing: 1.5px; }

/* 标题 */
.title-area { padding: 16px 20px 24px; }
.page-title { display: block; font-size: 30px; font-weight: 800; color: var(--ds-ink-1); letter-spacing: -0.5px; margin-bottom: 8px; }
.page-sub { display: block; font-size: 16px; color: var(--ds-ink-3); }

/* 表单 */
.form-card { margin: 0 20px; background: var(--ds-surface); border-radius: var(--ds-r-md); overflow: hidden; box-shadow: var(--ds-shadow-sm); border: 1px solid var(--ds-hairline); }
.field-item { display: flex; align-items: center; padding: 0 16px; min-height: 56px; gap: 12px; }
.field-ico { width: 24px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.field-input { flex: 1; font-size: 16px; color: var(--ds-ink-1); background: transparent; border: none; height: 56px; }
.field-input::placeholder { color: var(--ds-ink-4); }
.field-divider { height: 1px; background: var(--ds-hairline); margin-left: 52px; }
.field-action { padding: 8px 0 8px 12px; flex-shrink: 0; }
.action-text { font-size: 14px; font-weight: 600; color: var(--ds-brand); }

/* 错误 */
.error-area { padding: 12px 20px 0; }
.error-text { font-size: 13px; color: var(--ds-danger); }

/* 按钮 */
.btn-area { padding: 24px 20px 0; }
.primary-btn {
	height: 52px;
	border-radius: var(--ds-r-sm);
	background: var(--ds-grad-brand);
	box-shadow: var(--ds-shadow-brand);
	display: flex;
	align-items: center;
	justify-content: center;
	transition: transform 0.18s var(--ds-ease), box-shadow 0.18s var(--ds-ease), opacity 0.18s;
}
.primary-btn:active, .btn-pressed { transform: scale(0.97);  }
.primary-btn.disabled { opacity: 0.5; pointer-events: none; }
.btn-text { font-size: 17px; font-weight: 600; color: #fff; letter-spacing: 1px; }
.btn-spinner { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }

/* 链接 */
.link-area { display: flex; justify-content: center; align-items: center; gap: 4px; padding: 20px; }
.link-dim { font-size: 14px; color: var(--ds-ink-3); }
.link-blue { font-size: 14px; font-weight: 600; color: var(--ds-brand); }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
