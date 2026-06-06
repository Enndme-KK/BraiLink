/**
 * 登录状态管理工具
 */

// 检查是否已登录
export function isLoggedIn() {
	const token = uni.getStorageSync('token')
	const user = uni.getStorageSync('user')
	return !!(token && user)
}

// 获取当前用户信息
export function getCurrentUser() {
	return uni.getStorageSync('user') || null
}

// 获取当前用户类型
export function getCurrentUserType() {
	const user = getCurrentUser()
	return user ? user.user_type : null
}

// 获取token
export function getToken() {
	return uni.getStorageSync('token') || ''
}

// 保存登录信息
export function saveLoginInfo(token, user) {
	uni.setStorageSync('token', token)
	uni.setStorageSync('user', user)
	uni.setStorageSync('userType', user.user_type)
	uni.setStorageSync('userId', user.id) // 额外保存用户ID
}

// 清除登录信息
export function clearLoginInfo() {
	uni.removeStorageSync('token')
	uni.removeStorageSync('user')
	uni.removeStorageSync('userType')
	uni.removeStorageSync('userId') // 清除用户ID
}

// 检查登录状态并跳转
export function checkLoginAndRedirect() {
	if (!isLoggedIn()) {
		// 未登录，跳转到身份选择页
		return false
	}
	
	const userType = getCurrentUserType()
	if (userType === 'doctor') {
		uni.reLaunch({
			url: '/pages/managePatients/managePatients'
		})
		return true
	} else if (userType === 'patient') {
		uni.reLaunch({
			url: '/pages/medicalRecord/medicalRecord'
		})
		return true
	} else if (userType === 'family') {
		uni.reLaunch({
			url: '/pages/family/index'
		})
		return true
	}
	
	return false
}

// 需要登录才能访问的页面检查
export function requireAuth() {
	if (!isLoggedIn()) {
		uni.reLaunch({
			url: '/pages/selectIdentity/selectIdentity'
		})
		return false
	}
	return true
}
