// 导入环境配置
import ENV_CONFIG from '@/config/env.config.js'

// API配置 - 从环境配置中获取
const API_CONFIG = {
	BASE_URL: ENV_CONFIG.SERVER_URL,  // 服务器根URL（用于访问媒体文件）
	DJANGO_BASE_URL: ENV_CONFIG.DJANGO_BASE_URL,  // Django API URL
	FLASK_ML_URL: ENV_CONFIG.FLASK_ML_URL
}

// 获取token
const getToken = () => {
	return uni.getStorageSync('token') || ''
}

// 统一错误处理
const handleError = (error, reject) => {
	console.error('API Error:', error);
	uni.hideLoading();
	
	// 显示错误提示
	let errorMsg = '网络请求失败';
	if (error.errMsg) {
		if (error.errMsg.includes('timeout')) {
			errorMsg = '请求超时，请检查网络连接';
		} else if (error.errMsg.includes('fail')) {
			errorMsg = '无法连接到服务器，请检查网络连接';
		} else if (error.errMsg.includes('connect')) {
			errorMsg = '无法连接到服务器，请检查网络连接';
		}
	}
	
	// 不要在这里自动显示toast，让调用方决定如何显示错误
	// uni.showToast({
	// 	title: errorMsg,
	// 	icon: 'none',
	// 	duration: 2000
	// });
	
	reject(new Error(errorMsg));
}

// Django API请求
const djangoRequest = (url = '', data = {}, type = 'GET', header = {}) => {
	const token = getToken()
	const defaultHeader = {
		'Content-Type': 'application/json',
		'Authorization': token ? `Token ${token}` : ''
	}
	
		return new Promise((resolve, reject) => {
		// 新闻接口需要更长的超时时间（因为需要爬取和访问详情页）
		const isNewsAPI = url.includes('/home/news/')
		const timeout = isNewsAPI ? 120000 : 30000  // 新闻接口120秒，其他30秒
		
		uni.request({
			method: type,
			url: API_CONFIG.DJANGO_BASE_URL + url,
			data: data,
			header: { ...defaultHeader, ...header },
			dataType: 'json',
			timeout: timeout,
		}).then((response) => {
			setTimeout(function() {
				uni.hideLoading();
			}, 200);
			// 兼容两种 resolve 形式: 数组 [err, res] 或单 res 对象
			let error = null, res;
			if (Array.isArray(response)) {
				error = response[0];
				res = response[1];
			} else {
				res = response;
			}

			// 处理错误响应
			if (error) {
				handleError(error, reject);
				return;
			}
			if (!res) {
				handleError(new Error('空响应'), reject);
				return;
			}
			
			// 处理 HTTP 状态码
			if (res.statusCode === 401) {
				// token过期，清除本地存储
				uni.removeStorageSync('token')
				uni.removeStorageSync('user')
				uni.showToast({
					title: '登录已过期，请重新登录',
					icon: 'none',
					duration: 2000
				});
				setTimeout(() => {
					uni.reLaunch({
						url: '/pages/selectIdentity/selectIdentity'
					})
				}, 2000);
				reject(new Error('Unauthorized'));
				return;
			}
			
		if (res.statusCode >= 400) {
			// 服务器错误 - 返回完整的错误对象，让调用方处理
			console.log('[request.js] 服务器返回错误:', res.statusCode, res.data);
			
			let errorMsg = res.data?.message || res.data?.detail || '服务器错误';
			
			// 创建包含详细信息的错误对象
			const error = new Error(errorMsg);
			error.response = {
				status: res.statusCode,
				data: res.data
			};
			
			// 如果有详细的验证错误信息，不显示toast，让调用方处理
			if (res.data && typeof res.data === 'object' && Object.keys(res.data).length > 0) {
				reject(error);
			} else {
				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 2000
				});
				reject(error);
			}
			return;
		}
			
			resolve(res.data);
		}).catch(error => {
			// 兼容两种 reject 形式: 数组 [err, res] 或单 err 对象
			const err = Array.isArray(error) ? error[0] : error;
			handleError(err, reject);
		})
	});
}

// Flask ML API请求
const mlRequest = (url = '', data = {}, type = 'GET', header = {}) => {
	const token = getToken()
	const defaultHeader = {
		'Content-Type': 'application/json',
		'Authorization': token ? `Token ${token}` : '',
		...header
	}
	const timeout = url.includes('/capture_camera') ? 120000 : 60000
	
	return new Promise((resolve, reject) => {
		uni.request({
			method: type,
			url: API_CONFIG.FLASK_ML_URL + url,
			data: data,
			header: defaultHeader,
			dataType: 'json',
			timeout: timeout, // ML 服务可能需要更长时间
		}).then((response) => {
			setTimeout(function() {
				uni.hideLoading();
			}, 200);
			let error = null, res;
			if (Array.isArray(response)) {
				error = response[0];
				res = response[1];
			} else {
				res = response;
			}
			
			// 处理错误响应
			if (error) {
				handleError(error, reject);
				return;
			}
			if (!res) {
				handleError(new Error('空响应'), reject);
				return;
			}

			// 处理 HTTP 状态码
			if (res.statusCode === 401) {
				uni.removeStorageSync('token')
				uni.removeStorageSync('user')
				uni.showToast({ title: '登录已过期，请重新登录', icon: 'none', duration: 2000 })
				setTimeout(() => uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' }), 2000)
				reject(new Error('Unauthorized'))
				return
			}
			if (res.statusCode >= 400) {
				let errorMsg = res.data?.message || res.data?.error || res.data?.response || 'ML服务错误'
				reject(new Error(errorMsg))
				return;
			}
			
			resolve(res.data);
		}).catch(error => {
			const err = Array.isArray(error) ? error[0] : error;
			handleError(err, reject);
		})
	});
}

// 用户认证相关API
export const authAPI = {
	// 用户注册
	register: (data) => djangoRequest('/auth/register/', data, 'POST'),
	// 用户登录
	login: (data) => djangoRequest('/auth/login/', data, 'POST'),
	// 用户登出
	logout: () => djangoRequest('/auth/logout/', {}, 'POST'),
	// 获取用户信息
	getProfile: () => djangoRequest('/auth/profile/'),
	// 更新用户信息
	updateProfile: (data) => djangoRequest('/auth/update-profile/', data, 'PUT'),
	// 修改密码
	changePassword: (data) => djangoRequest('/auth/change-password/', data, 'POST'),
	// 提交意见反馈
	submitFeedback: (data) => djangoRequest('/auth/feedback/', data, 'POST')
}

// 病人相关API
export const patientAPI = {
	// 获取病人列表
	getPatients: () => djangoRequest('/patients/'),
	// 获取我的档案
	getMyProfile: () => djangoRequest('/patients/my_profile/'),
	// 创建/更新档案
	createProfile: (data) => djangoRequest('/patients/', data, 'POST'),
	// 更新档案
	updateProfile: (id, data) => djangoRequest(`/patients/${id}/`, data, 'PUT'),
	// 生成家属绑定邀请码
	generateFamilyInviteCode: () => djangoRequest('/families/generate_invite_code/', {}, 'POST')
}

// 家属相关API
export const familyAPI = {
	// 获取我的家属档案
	getMyProfile: () => djangoRequest('/families/my_profile/'),
	// 获取我的绑定关系
	getMyBindings: () => djangoRequest('/families/my_bindings/'),
	// 获取家属首页摘要
	getHomeSummary: () => djangoRequest('/families/home_summary/'),
	// 获取关联医生列表
	getRelatedDoctors: () => djangoRequest('/families/related_doctors/'),
	// 通过邀请码绑定病人
	bindByInviteCode: (data) => djangoRequest('/families/bind_by_invite_code/', data, 'POST'),
	// 解除家属与患者绑定
	unbindPatient: (data) => djangoRequest('/families/unbind_patient/', data, 'POST')
}

// 医生相关API
export const doctorAPI = {
	// 获取医生列表
	getDoctors: () => djangoRequest('/doctors/'),
	// 获取我的档案
	getMyProfile: () => djangoRequest('/doctors/my_profile/'),
	// 创建/更新档案
	createProfile: (data) => djangoRequest('/doctors/', data, 'POST'),
	// 更新档案
	updateProfile: (id, data) => djangoRequest(`/doctors/${id}/`, data, 'PUT'),
	// 获取该医生接诊过的患者所绑定的家属列表
	getRelatedFamilies: () => djangoRequest('/doctors/related_families/')
}

// 医疗记录相关API
export const medicalRecordAPI = {
	// 获取医疗记录列表
	getRecords: () => djangoRequest('/medical-records/'),
	// 获取单个医疗记录
	getRecord: (id) => djangoRequest(`/medical-records/${id}/`),
	// 创建医疗记录
	createRecord: (data) => djangoRequest('/medical-records/', data, 'POST'),
	// 删除医疗记录
	deleteRecord: (id) => djangoRequest(`/medical-records/${id}/`, {}, 'DELETE'),
	// 更新医疗记录
	updateRecord: (id, data) => djangoRequest(`/medical-records/${id}/`, data, 'PATCH'),
	// 上传CT扫描（与后端字段 original_image 对齐）
	uploadCTScan: (id, data) => {
		return new Promise((resolve, reject) => {
			const token = getToken()
			uni.uploadFile({
				url: `${API_CONFIG.DJANGO_BASE_URL}/medical-records/${id}/upload_ct_scan/`,
				filePath: data.imagePath,
				name: 'original_image',
				formData: {
					'scan_mode': data.scanMode || 't1'
				},
				header: {
					'Authorization': token ? `Token ${token}` : ''
				},
				success: (res) => {
					try { resolve(JSON.parse(res.data)) } catch (e) { resolve(res.data) }
				},
				fail: reject
			})
		})
	},
	// 获取CT扫描结果
	getCTScans: (id) => djangoRequest(`/medical-records/${id}/ct_scans/`),
	// 为已有原图的病历补生成AI分割图
	reanalyzeCTScans: (id, data = {}) => djangoRequest(`/medical-records/${id}/reanalyze_ct_scans/`, data, 'POST'),
	// 验证CT扫描
	verifyCTScan: (id, data) => djangoRequest(`/medical-records/${id}/verify_ct_scan/`, data, 'PUT'),
	// 医生接诊病历
	assignToMe: (id) => djangoRequest(`/medical-records/${id}/assign_to_me/`, {}, 'POST'),
	// 生成Word格式报告
	generateWordReport: (data) => djangoRequest('/medical-records/generate_word_report/', data, 'POST')
}

// 预约挂号相关API
export const appointmentAPI = {
	// 创建挂号申请（患者端）
	createAppointment: (data) => djangoRequest('/appointments/', data, 'POST'),
	// 当前用户的挂号记录
	getMyAppointments: () => djangoRequest('/appointments/my_appointments/'),
	// 医生待接诊挂号
	getDoctorPending: () => djangoRequest('/appointments/doctor_pending/'),
	// 家属绑定患者的挂号记录
	getFamilyAppointments: () => djangoRequest('/appointments/family_appointments/'),
	// 医生接诊
	acceptAppointment: (id) => djangoRequest(`/appointments/${id}/accept/`, {}, 'POST'),
	// 医生拒绝
	rejectAppointment: (id, data = {}) => djangoRequest(`/appointments/${id}/reject/`, data, 'POST'),
	// 患者取消
	cancelAppointment: (id) => djangoRequest(`/appointments/${id}/cancel/`, {}, 'POST'),
	// 医生完成就诊
	completeAppointment: (id) => djangoRequest(`/appointments/${id}/complete/`, {}, 'POST')
}

// AI聊天相关API
export const chatAPI = {
	// 获取聊天会话列表
	getSessions: () => djangoRequest('/ai-chat/'),
	// 获取单个会话
	getSession: (id) => djangoRequest(`/ai-chat/${id}/`),
	// 创建新会话
	createSession: (data) => djangoRequest('/ai-chat/', data, 'POST'),
	// 发送消息
	sendMessage: (id, data) => djangoRequest(`/ai-chat/${id}/send_message/`, data, 'POST'),
	// 获取会话消息
	getMessages: (id) => djangoRequest(`/ai-chat/${id}/messages/`),
	// 更新会话标题
	updateTitle: (id, data) => djangoRequest(`/ai-chat/${id}/update_title/`, data, 'PUT')
}

// ML服务相关API
export const mlAPI = {
	// 分析CT图像（MRI分割）
	analyzeCT: (data) => {
		return new Promise((resolve, reject) => {
			const token = getToken()
			console.log('[mlAPI.analyzeCT] 请求:', data)
			uni.uploadFile({
				url: `${API_CONFIG.FLASK_ML_URL}/analyze_ct`,
				filePath: data.imagePath,
				name: 'image',
				formData: {
					'scan_mode': data.scanMode
				},
				header: {
					'Authorization': token ? `Token ${token}` : ''
				},
				success: (res) => {
					console.log('[mlAPI.analyzeCT] 原始响应 statusCode:', res.statusCode, 'data:', res.data)
					try {
						const parsed = JSON.parse(res.data)
						console.log('[mlAPI.analyzeCT] 解析结果:', parsed)
						resolve(parsed)
					} catch (e) {
						console.error('[mlAPI.analyzeCT] JSON解析失败:', e, '原始数据:', res.data)
						reject(new Error('服务器返回数据格式错误'))
					}
				},
				fail: (err) => {
					console.error('[mlAPI.analyzeCT] 请求失败:', err)
					reject(err)
				}
			})
		})
	},

	// 调用后端USB相机拍照，并直接执行MRI分割
	captureCamera: (data = {}) => mlRequest('/capture_camera', data, 'POST'),
	
	// AI聊天（增强版）
	// 支持传入患者信息和扫描结果
	chat: (data) => {
		const chatData = {
			messages: data.messages || [],
			patient_info: data.patient_info || {},
			scan_result: data.scan_result || null
		}
		return mlRequest('/chat', chatData, 'POST')
	},
	
	// 快速问答（简化版聊天接口）
	quickChat: (question, patientInfo = {}) => {
		return mlRequest('/chat', {
			messages: [
				{ role: 'user', content: question }
			],
			patient_info: patientInfo
		}, 'POST')
	},
	
	// 带扫描结果的咨询
	chatWithScanResult: (question, scanResult, patientInfo = {}) => {
		return mlRequest('/chat', {
			messages: [
				{ role: 'user', content: question }
			],
			patient_info: patientInfo,
			scan_result: scanResult
		}, 'POST')
	},
	
	// 健康检查
	healthCheck: () => mlRequest('/health'),
	
	// 模型信息
	getModelInfo: () => mlRequest('/model_info')
}

// 通知相关API
export const notificationAPI = {
	// 获取通知列表
	getNotifications: () => djangoRequest('/notifications/'),
	// 获取聊天会话列表（按对话对象分组）
	getChatSessions: () => djangoRequest('/notifications/chat_sessions/'),
	// 获取聊天消息（双向：发送+接收）
	// partnerId: 可选，对话对象的用户ID，如果提供则只返回与该对象的对话
	getChatMessages: (partnerId) => {
		if (partnerId) {
			return djangoRequest(`/notifications/chat_messages/?partner_id=${partnerId}`)
		}
		return djangoRequest('/notifications/chat_messages/')
	},
	// 获取未读通知数量
	getUnreadCount: () => djangoRequest('/notifications/unread_count/'),
	// 标记通知为已读
	markRead: (id) => djangoRequest(`/notifications/${id}/mark_read/`, {}, 'POST'),
	// 标记所有通知为已读
	markAllRead: () => djangoRequest('/notifications/mark_all_read/', {}, 'POST'),
	// 发送聊天消息（医生和患者都可以使用）
	sendChatMessage: (data) => djangoRequest('/notifications/send_chat_message/', data, 'POST'),
	// 发送通知给患者（医生端，保留兼容性）
	sendToPatient: (data) => djangoRequest('/notifications/send_to_patient/', data, 'POST')
}

// 首页相关API
export const homeAPI = {
	// 获取医学界新闻
	getMedicalNews: (params = {}) => djangoRequest('/medical-records/home/news/', params),
	// 获取今日就诊患者（医生端）
	getTodayPatients: () => djangoRequest('/medical-records/home/today-patients/')
}

// 导出 API 配置，方便其他地方使用
export { API_CONFIG }

export default {
	djangoRequest,
	mlRequest,
	authAPI,
	patientAPI,
	familyAPI,
	doctorAPI,
	medicalRecordAPI,
	appointmentAPI,
	chatAPI,
	mlAPI,
	notificationAPI,
	homeAPI,
	API_CONFIG
}
