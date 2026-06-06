<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-placeholder"></view>
				<text class="nav-title">消息中心</text>
				<view class="nav-action" v-if="activeTab === 'notice' && unreadCount > 0" @click="markAllRead" hover-class="back-pressed">
					<text class="action-text">全部已读</text>
				</view>
				<view v-else class="nav-placeholder"></view>
			</view>
		</view>

		<!-- Tab 导航 -->
		<view class="tab-bar">
			<view class="tab-item" :class="{ active: activeTab === 'notice' }" @click="activeTab = 'notice'">
				<text class="tab-text">系统通知</text>
				<view class="tab-badge" v-if="unreadCount > 0"><text class="badge-num">{{ unreadCount > 99 ? '99+' : unreadCount }}</text></view>
			</view>
			<view class="tab-item" :class="{ active: activeTab === 'chat' }" @click="switchToChat">
				<text class="tab-text">聊天消息</text>
				<view class="tab-badge" v-if="chatUnread > 0"><text class="badge-num">{{ chatUnread > 99 ? '99+' : chatUnread }}</text></view>
			</view>
		</view>

		<!-- 系统通知 Tab -->
		<view v-show="activeTab === 'notice'">
			<view class="loading-block" v-if="loading">
				<view class="ds-spinner"></view>
				<text class="loading-text">加载通知中...</text>
			</view>

			<view class="content" v-else-if="notifications.length > 0">
				<view class="notification-card" :class="{ unread: !item.is_read }" v-for="item in notifications" :key="item.id" @click="handleNoticeClick(item)" hover-class="card-pressed">
					<view class="card-head">
						<view class="head-left">
							<view class="dot-unread" v-if="!item.is_read"></view>
							<text class="card-title">{{ item.title }}</text>
						</view>
						<text class="card-time ds-mono">{{ formatTime(item.created_at) }}</text>
					</view>
					<text class="card-content">{{ item.content }}</text>
					<view class="card-footer">
						<text class="footer-sender" v-if="item.sender_info">来自 {{ item.sender_info.name || item.sender_info.username }}</text>
						<view class="footer-action" v-if="item.medical_record_id">
							<text class="action-text-link">查看报告</text>
							<text class="action-arrow">›</text>
						</view>
					</view>
				</view>
			</view>

			<view class="empty-state" v-else>
				<view class="empty-ico">
					<svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#A2A9BC" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M18 16v-5a6 6 0 0 0-12 0v5l-2 2v1h16v-1l-2-2z"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>
				</view>
				<text class="empty-title">当前暂无通知</text>
				<text class="empty-desc">有新消息时会在此显示</text>
			</view>
		</view>

		<!-- 聊天消息 Tab -->
		<view v-show="activeTab === 'chat'">
			<view class="loading-block" v-if="chatLoading">
				<view class="ds-spinner"></view>
				<text class="loading-text">加载会话中...</text>
			</view>

			<view class="content" v-else-if="chatSessions.length > 0">
				<view class="chat-card" v-for="session in chatSessions" :key="session.partner_id" @click="openChat(session)" hover-class="card-pressed">
					<view class="chat-avatar">
						<text class="chat-avatar-text">{{ getInitial(session.partner_name) }}</text>
					</view>
					<view class="chat-body">
						<view class="chat-top-row">
							<text class="chat-name">{{ session.partner_name }}</text>
							<view class="chat-role-tag" :class="session.partner_role">
								<text class="chat-role-text">{{ getRoleLabel(session.partner_role) }}</text>
							</view>
						</view>
						<text class="chat-last-msg">{{ session.last_message || '暂无消息' }}</text>
					</view>
					<view class="chat-meta">
						<text class="chat-time ds-mono">{{ formatTime(session.last_time) }}</text>
						<view class="chat-unread-dot" v-if="session.unread > 0">
							<text class="chat-unread-num">{{ session.unread }}</text>
						</view>
					</view>
				</view>
			</view>

			<view class="empty-state" v-else>
				<view class="empty-ico">
					<svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#A2A9BC" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 20l1-4a8.5 8.5 0 0 1-1-4 8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5z"/></svg>
				</view>
				<text class="empty-title">暂无聊天会话</text>
				<text class="empty-desc">与医生或患者的对话会在此显示</text>
			</view>
		</view>

		<bottom-nav-doctor v-if="userType === 'doctor'" current="messages" />
		<bottom-nav-patient v-else-if="userType === 'patient'" current="messages" />
		<bottom-nav-family v-else-if="userType === 'family'" current="messages" />
	</view>
</template>

<script>
import { notificationAPI } from '@/utils/request.js'
import BottomNavDoctor from '@/components/bottom_nav/BottomNavDoctor.vue'
import BottomNavPatient from '@/components/bottom_nav/BottomNavPatient.vue'
import BottomNavFamily from '@/components/bottom_nav/BottomNavFamily.vue'

export default {
	components: { BottomNavDoctor, BottomNavPatient, BottomNavFamily },
	data() {
		return {
			userType: 'patient',
			activeTab: 'notice',
			loading: false,
			notifications: [],
			unreadCount: 0,
			chatLoading: false,
			chatSessions: [],
			chatUnread: 0
		}
	},
	async onLoad() {
		const user = uni.getStorageSync('user')
		if (user && user.user_type) this.userType = user.user_type
		await this.loadNotifications()
	},
	async onShow() { await this.loadNotifications(); if (this.activeTab === 'chat') await this.loadChatSessions() },
	methods: {
		async switchToChat() {
			this.activeTab = 'chat'
			if (this.chatSessions.length === 0) await this.loadChatSessions()
		},
		async loadNotifications() {
			try {
				this.loading = true
				const response = await notificationAPI.getNotifications()
				const all = Array.isArray(response) ? response : (response.results || [])
				// 系统通知 tab 只显示非聊天类型的通知
				this.notifications = all.filter(n => n.notification_type !== 'chat' && n.notification_type !== 'message')
				this.unreadCount = this.notifications.filter(n => !n.is_read).length
			} catch (e) {
				uni.showToast({ title: '加载通知失败', icon: 'none' })
			} finally { this.loading = false }
		},
		async loadChatSessions() {
			try {
				this.chatLoading = true
				const response = await notificationAPI.getChatSessions()
				this.chatSessions = Array.isArray(response) ? response : (response.results || response.sessions || [])
				this.chatUnread = this.chatSessions.reduce((sum, s) => sum + (s.unread || 0), 0)
			} catch (e) {
				// 后端可能还没有 chat_sessions 接口，降级用 notifications 中的 chat 类型
				try {
					const all = Array.isArray(this.notifications) ? this.notifications : []
					const chatNotices = all.filter(n => n.notification_type === 'chat' || n.notification_type === 'message')
					const sessionMap = {}
					chatNotices.forEach(n => {
						const partnerId = n.sender_info?.id || n.sender
						if (!partnerId) return
						if (!sessionMap[partnerId]) {
							sessionMap[partnerId] = {
								partner_id: partnerId,
								partner_name: n.sender_info?.name || n.sender_info?.username || '未知',
								partner_role: n.sender_info?.user_type || 'doctor',
								last_message: n.content,
								last_time: n.created_at,
								unread: n.is_read ? 0 : 1
							}
						} else {
							sessionMap[partnerId].unread += n.is_read ? 0 : 1
							if (new Date(n.created_at) > new Date(sessionMap[partnerId].last_time)) {
								sessionMap[partnerId].last_message = n.content
								sessionMap[partnerId].last_time = n.created_at
							}
						}
					})
					this.chatSessions = Object.values(sessionMap).sort((a, b) => new Date(b.last_time) - new Date(a.last_time))
					this.chatUnread = this.chatSessions.reduce((sum, s) => sum + (s.unread || 0), 0)
				} catch (e2) { this.chatSessions = [] }
			} finally { this.chatLoading = false }
		},
		openChat(session) {
			const pid = session.partner_id || ""
			if (!pid) { uni.showToast({ title: "会话信息不完整", icon: "none" }); return }
			uni.navigateTo({
				url: `/pages/chat/chatDialog?partner_id=${pid}&partner_role=${session.partner_role}&partner_name=${encodeURIComponent(session.partner_name)}`
			})
		},
		async handleNoticeClick(notification) {
			try {
				if (!notification.is_read) {
					await notificationAPI.markRead(notification.id)
					notification.is_read = true
					this.unreadCount = Math.max(0, this.unreadCount - 1)
				}
				if (notification.notification_type === 'chat' || notification.notification_type === 'message') {
					const senderId = notification.sender_info?.id || ''
					const senderName = notification.sender_info?.name || notification.sender_info?.username || '对方'
					const senderRole = notification.sender_info?.user_type || 'doctor'
					if (!senderId) { uni.showToast({ title: "发送者信息缺失", icon: "none" }); return }
					uni.navigateTo({ url: `/pages/chat/chatDialog?partner_id=${senderId}&partner_role=${senderRole}&partner_name=${encodeURIComponent(senderName)}` })
				} else if (notification.medical_record_id) {
					try {
						const { medicalRecordAPI } = await import('@/utils/request.js')
						const record = await medicalRecordAPI.getRecord(notification.medical_record_id)
						const hasCT = Array.isArray(record?.ct_scans) && record.ct_scans.length > 0
						if (hasCT) {
							uni.navigateTo({ url: `/pages/previewReport/previewReport?recordId=${notification.medical_record_id}` })
						} else {
							uni.showModal({ title: notification.title, content: notification.content, showCancel: false })
						}
					} catch (e) { uni.showToast({ title: '获取病历失败', icon: 'none' }) }
				} else {
					uni.showModal({ title: notification.title, content: notification.content, showCancel: false })
				}
			} catch (e) { uni.showToast({ title: '操作失败', icon: 'none' }) }
		},
		async markAllRead() {
			try {
				uni.showLoading({ title: '处理中...', mask: true })
				await notificationAPI.markAllRead()
				this.notifications.forEach(n => { n.is_read = true })
				this.unreadCount = 0
				uni.hideLoading()
				uni.showToast({ title: '已全部标记为已读', icon: 'success' })
			} catch (e) {
				uni.hideLoading()
				uni.showToast({ title: '操作失败', icon: 'none' })
			}
		},
		getInitial(name) { return name ? String(name).slice(0, 1) : '?' },
		getRoleLabel(role) { return { doctor: '医生', patient: '患者', family: '家属' }[role] || role || '' },
		formatTime(timeStr) {
			if (!timeStr) return ''
			const date = new Date(timeStr); const now = new Date()
			const diff = now - date
			const minutes = Math.floor(diff / 60000), hours = Math.floor(minutes / 60), days = Math.floor(hours / 24)
			if (days > 0) {
				if (days === 1) return '昨天'
				if (days < 7) return `${days}天前`
				return `${date.getMonth()+1}-${String(date.getDate()).padStart(2,'0')}`
			}
			if (hours > 0) return `${hours}小时前`
			if (minutes > 0) return `${minutes}分钟前`
			return '刚刚'
		}
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); font-family: var(--ds-font); padding-bottom: 80px; }
.navbar { position: sticky; top: 0; z-index: 100; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.82); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; display: flex; align-items: center; justify-content: space-between; padding: 52px 16px 12px; }
.nav-title { font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-action { padding: 6px 12px; border-radius: var(--ds-r-pill); background: var(--ds-brand-soft); }
.action-text { font-size: 13px; font-weight: 600; color: var(--ds-brand); }
.nav-placeholder { width: 36px; }

/* Tab Bar */
.tab-bar { display: flex; padding: 12px 20px 0; gap: 0; background: var(--ds-bg); }
.tab-item { flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 10px 0 12px; position: relative; transition: all 0.2s; }
.tab-item.active::after { content: ''; position: absolute; bottom: 0; left: 30%; right: 30%; height: 3px; border-radius: 2px; background: var(--ds-brand); }
.tab-text { font-size: 15px; font-weight: 600; color: var(--ds-ink-3); transition: color 0.2s; }
.tab-item.active .tab-text { color: var(--ds-ink-1); }
.tab-badge { min-width: 18px; height: 18px; border-radius: 9px; background: var(--ds-danger); display: flex; align-items: center; justify-content: center; padding: 0 5px; }
.badge-num { font-size: 10px; font-weight: 700; color: #fff; }

/* Shared */
.loading-block { display: flex; flex-direction: column; align-items: center; padding: 80px 0; gap: 14px; }
.loading-text { font-size: 13px; color: var(--ds-ink-3); }
.content { padding: 16px 20px 30px; }

/* Notification Cards */
.notification-card { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 16px; margin-bottom: 12px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); transition: all 0.18s var(--ds-ease); }
.notification-card.unread { border-left: 3px solid var(--ds-brand); background: var(--ds-brand-soft); }
.card-pressed { transform: scale(0.99); }
.card-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; gap: 10px; }
.head-left { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0; }
.dot-unread { width: 7px; height: 7px; border-radius: 50%; background: var(--ds-brand); flex-shrink: 0; box-shadow: 0 0 0 0 rgba(10,92,255,0.4); animation: pulse-blue 2s infinite; }
@keyframes pulse-blue { 0% { box-shadow: 0 0 0 0 rgba(10,92,255,0.4); } 70% { box-shadow: 0 0 0 6px rgba(10,92,255,0); } 100% { box-shadow: 0 0 0 0 rgba(10,92,255,0); } }
.card-title { font-size: 15px; font-weight: 700; color: var(--ds-ink-1); flex: 1; min-width: 0; }
.card-time { font-size: 11px; color: var(--ds-ink-4); letter-spacing: 0.3px; flex-shrink: 0; }
.card-content { display: block; font-size: 13px; line-height: 1.6; color: var(--ds-ink-2); margin-bottom: 10px; -webkit-line-clamp: 3; overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; }
.card-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 10px; border-top: 1px solid var(--ds-hairline); }
.footer-sender { font-size: 11px; color: var(--ds-ink-3); }
.footer-action { display: flex; align-items: center; gap: 4px; }
.action-text-link { font-size: 12px; font-weight: 600; color: var(--ds-brand); }
.action-arrow { font-size: 16px; color: var(--ds-brand); line-height: 1; }

/* Chat Session Cards */
.chat-card { display: flex; align-items: center; gap: 12px; background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 14px 16px; margin-bottom: 10px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); transition: all 0.18s; }
.chat-avatar { width: 44px; height: 44px; border-radius: 14px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.chat-avatar-text { font-size: 17px; font-weight: 700; color: #fff; }
.chat-body { flex: 1; min-width: 0; }
.chat-top-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.chat-name { font-size: 15px; font-weight: 700; color: var(--ds-ink-1); }
.chat-role-tag { padding: 2px 8px; border-radius: var(--ds-r-pill); }
.chat-role-tag.doctor { background: var(--ds-brand-soft); }
.chat-role-tag.patient { background: rgba(31,184,119,0.12); }
.chat-role-tag.family { background: rgba(245,166,35,0.12); }
.chat-role-text { font-size: 10px; font-weight: 700; }
.chat-role-tag.doctor .chat-role-text { color: var(--ds-brand); }
.chat-role-tag.patient .chat-role-text { color: #1FB877; }
.chat-role-tag.family .chat-role-text { color: #F5A623; }
.chat-last-msg { font-size: 13px; color: var(--ds-ink-3); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chat-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.chat-time { font-size: 11px; color: var(--ds-ink-4); }
.chat-unread-dot { min-width: 18px; height: 18px; border-radius: 9px; background: var(--ds-danger); display: flex; align-items: center; justify-content: center; padding: 0 5px; }
.chat-unread-num { font-size: 10px; font-weight: 700; color: #fff; }

/* Empty */
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 80px 20px; gap: 12px; }
.empty-ico { width: 80px; height: 80px; border-radius: 24px; background: var(--ds-surface); display: flex; align-items: center; justify-content: center; box-shadow: var(--ds-shadow-sm); }
.empty-title { font-size: 16px; font-weight: 700; color: var(--ds-ink-2); }
.empty-desc { font-size: 13px; color: var(--ds-ink-4); }
</style>
