<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack" hover-class="back-pressed">
					<text class="back-char">‹</text>
				</view>
				<view class="nav-center">
					<text class="nav-title">{{ chatPartner }}</text>
					<view class="subtitle-row">
						<text class="nav-subtitle">{{ chatSubtitle }}</text>
						<view class="role-pill family" v-if="showFamilyBadge"><text class="role-pill-text">家属</text></view>
					</view>
				</view>
				<view class="nav-placeholder"></view>
			</view>
		</view>

		<!-- 快捷话术 -->
		<view class="quick-panel" v-if="showQuickTemplates">
			<view class="quick-head">
				<text class="quick-title">病情沟通快捷话术</text>
				<text class="quick-tip">点击即可填入输入框</text>
			</view>
			<scroll-view class="quick-scroll" scroll-x show-scrollbar="false">
				<view class="quick-track">
					<view class="quick-chip" v-for="(template, index) in quickTemplates" :key="index" @click="applyQuickTemplate(template)" hover-class="chip-pressed">
						<text class="quick-chip-text">{{ template.label }}</text>
					</view>
				</view>
			</scroll-view>
		</view>

		<scroll-view class="messages-area" scroll-y :scroll-top="scrollTop" scroll-with-animation>
			<view class="loading-block" v-if="loading">
				<view class="ds-spinner"></view>
				<text class="loading-text">加载消息中...</text>
			</view>

			<view class="empty-state" v-else-if="messages.length === 0">
				<view class="empty-ico">
					<svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#A2A9BC" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 20l1-4a8.5 8.5 0 0 1-1-4 8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5z"/></svg>
				</view>
				<text class="empty-text">暂无消息</text>
				<text class="empty-desc">开始一段对话吧</text>
			</view>

			<view class="msg-list" v-else>
				<view class="msg-item" v-for="(msg, index) in messages" :key="msg.id || index" :class="{ mine: msg.is_mine, other: !msg.is_mine }">
					<view class="msg-avatar">
						<text class="avatar-text">{{ getAvatarText(msg.sender_name) }}</text>
					</view>
					<view class="msg-bubble-wrap">
						<view class="msg-info">
							<text class="sender-name">{{ msg.sender_name }}</text>
							<text class="msg-time ds-mono">{{ formatTime(msg.created_at) }}</text>
						</view>
						<view class="msg-bubble">
							<text class="msg-text">{{ msg.content }}</text>
						</view>
					</view>
				</view>
			</view>
			<view style="height: 16px;"></view>
		</scroll-view>

		<view class="input-bar">
			<view class="input-wrap">
				<input class="msg-input" v-model="messageText" placeholder="输入消息..." placeholder-class="ph" :adjust-position="true" @confirm="sendMessage" />
			</view>
			<view class="send-btn" :class="{ active: messageText.trim() }" @click="sendMessage" hover-class="send-pressed">
				<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2 11 13"/><path d="M22 2l-7 20-4-9-9-4z"/></svg>
			</view>
		</view>
	</view>
</template>

<script>
import { notificationAPI } from '@/utils/request.js'

export default {
	data() {
		return {
			patientId: '', patientName: '', chatPartner: '', chatSubtitle: '',
			isDoctor: false, currentUserId: '', recipientUserId: '', partnerRole: '',
			messages: [], messageText: '', loading: false, scrollTop: 0, refreshInterval: null,
			quickTemplates: [
				{ label: '病情说明', content: '您好，我先向您同步一下患者目前的病情进展：当前检查结果和临床表现我已结合评估，如有新的不适或指标变化，请及时告诉我。' },
				{ label: '检查安排', content: '关于后续检查安排，建议您按预约时间带患者完成相关检查；检查前如有用药、饮食或休息方面的问题，也可以继续留言说明。' },
				{ label: '注意事项', content: '近期请重点观察患者精神状态、疼痛变化、睡眠及饮食情况；如果出现明显加重、持续头痛、呕吐或意识异常，请尽快就医。' },
				{ label: '复诊提醒', content: '建议按计划复诊，并携带既往检查资料一并来院，方便我持续评估病情变化和后续治疗方案。' }
			]
		}
	},
	computed: {
		showFamilyBadge() { return this.partnerRole === 'family' },
		showQuickTemplates() { return this.isDoctor && this.partnerRole === 'family' }
	},
	onLoad(options) {
		import('@/utils/auth.js').then(module => {
			if (!module.requireAuth()) return
			const userType = module.getCurrentUserType()
			this.isDoctor = userType === 'doctor'
			this.partnerRole = options.partner_role || ''
			this.patientName = options.patient_name ? decodeURIComponent(options.patient_name) : ''
			const relationship = options.relationship ? decodeURIComponent(options.relationship) : ''
			// 统一提取接收者ID：trim 掉空字符串，按优先级取第一个有效值
			const rawPid = (options.partner_user_id || options.partner_id || options.patient_id || '').trim()
			if (rawPid) {
				if (options.patient_id && options.patient_id.trim() === rawPid) this.patientId = rawPid
				this.recipientUserId = rawPid
			}
			if (options.partner_name) this.chatPartner = decodeURIComponent(options.partner_name)
			else if (options.patient_name) this.chatPartner = decodeURIComponent(options.patient_name)
			else this.chatPartner = this.getDefaultPartnerName(userType)
			this.currentUserId = this.getCurrentUserId()
			this.chatSubtitle = this.buildSubtitle(userType, relationship)
			this.loadMessages()
			this.refreshInterval = setInterval(() => this.loadMessages(true), 3000)
		})
	},
	onUnload() { if (this.refreshInterval) clearInterval(this.refreshInterval) },
	methods: {
		getCurrentUserId() {
			let id = uni.getStorageSync('userId')
			if (!id) { const u = uni.getStorageSync('user'); if (u && u.id) id = u.id }
			return id
		},
		getDefaultPartnerName(userType) {
			if (userType === 'doctor') return '患者'
			if (userType === 'family') return '医生'
			return '医生'
		},
		buildSubtitle(userType, relationship) {
			if (userType === 'family') return relationship ? `家属 · ${relationship}` : '家属与医生沟通'
			if (this.partnerRole === 'family') {
				const r = relationship ? ` · ${relationship}` : ''
				const p = this.patientName ? ` · 关于 ${this.patientName}` : ''
				return `家属${r}${p}`
			}
			if (this.partnerRole === 'doctor') return '医生'
			if (this.partnerRole === 'patient') return '患者'
			return userType === 'doctor' ? '患者' : '医生'
		},
		applyQuickTemplate(template) { this.messageText = template.content },
		async loadMessages(silent = false) {
			if (!silent) this.loading = true
			try {
				const response = await notificationAPI.getChatMessages(this.recipientUserId)
				let all = []
				if (response) {
					if (Array.isArray(response)) all = response
					else if (response.results && Array.isArray(response.results)) all = response.results
				}
				this.messages = all
					.filter(msg => {
						if (msg.notification_type !== 'message' && msg.notification_type !== 'chat') return false
						if (!this.recipientUserId) return true
						const senderId = msg.sender_info ? String(msg.sender_info.id) : ''
						const recipientId = msg.recipient_info ? String(msg.recipient_info.id) : ''
						const me = String(this.currentUserId || '')
						const partner = String(this.recipientUserId || '')
						return (senderId === me && recipientId === partner) || (senderId === partner && recipientId === me)
					})
					.map(msg => {
						const senderId = msg.sender_info ? String(msg.sender_info.id) : ''
						const isMine = senderId === String(this.currentUserId || '')
						let senderName = '未知'
						if (msg.sender_display_name) senderName = msg.sender_display_name
						else if (msg.sender_info) senderName = msg.sender_info.name || msg.sender_info.username
						if (!isMine && msg.sender_user_type === 'family') senderName = `${senderName}（家属）`
						return {
							id: msg.id, content: msg.content, sender_name: senderName, created_at: msg.created_at,
							is_mine: isMine, is_read: msg.is_read,
							sender_id: msg.sender_info ? msg.sender_info.id : null,
							recipient_id: msg.recipient_info ? msg.recipient_info.id : null
						}
					})
					.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
				await this.markMessagesAsRead()
				this.$nextTick(() => this.scrollToBottom())
			} catch (error) {
				if (!silent) uni.showToast({ title: error?.response?.data?.error || '加载消息失败', icon: 'none' })
			} finally { this.loading = false }
		},
		async markMessagesAsRead() {
			const unread = this.messages.filter(msg => !msg.is_mine && !msg.is_read)
			for (const msg of unread) { try { await notificationAPI.markRead(msg.id) } catch (e) {} }
		},
		async sendMessage() {
			if (!this.messageText.trim()) { uni.showToast({ title: '请输入消息内容', icon: 'none' }); return }
			if (!this.recipientUserId) { uni.showToast({ title: '接收者信息缺失', icon: 'none' }); return }
			try {
				await notificationAPI.sendChatMessage({ recipient_id: this.recipientUserId, content: this.messageText.trim() })
				this.messageText = ''
				await this.loadMessages(true)
			} catch (error) {
				uni.showToast({ title: error?.response?.data?.error || '发送失败', icon: 'none' })
			}
		},
		getAvatarText(name) { return name ? name.replace('（家属）', '').slice(0, 1) : '?' },
		scrollToBottom() { this.scrollTop = 9999999 },
		formatTime(timeStr) {
			if (!timeStr) return ''
			const date = new Date(timeStr); const now = new Date(); const diff = now - date
			if (diff < 60000) return '刚刚'
			if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
			if (date.toDateString() === now.toDateString()) return `今天 ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
			const yest = new Date(now); yest.setDate(yest.getDate() - 1)
			if (date.toDateString() === yest.toDateString()) return `昨天 ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
			return `${date.getMonth()+1}-${String(date.getDate()).padStart(2,'0')} ${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`
		},
		goBack() { uni.navigateBack() }
	}
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: var(--ds-bg); font-family: var(--ds-font); overflow: hidden; }

.navbar { position: relative; flex-shrink: 0; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; display: flex; align-items: center; justify-content: space-between; padding: 52px 16px 12px; gap: 10px; }
.nav-back { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; flex-shrink: 0; }
.back-pressed { background: var(--ds-brand-ghost); }
.back-char { font-size: 32px; font-weight: 300; color: var(--ds-brand); line-height: 1; margin-top: -4px; }
.nav-center { flex: 1; min-width: 0; text-align: center; }
.nav-title { display: block; font-size: 16px; font-weight: 700; color: var(--ds-ink-1); }
.subtitle-row { display: flex; justify-content: center; align-items: center; gap: 6px; margin-top: 2px; }
.nav-subtitle { font-size: 11px; color: var(--ds-ink-3); }
.role-pill { padding: 1px 7px; border-radius: var(--ds-r-pill); }
.role-pill.family { background: rgba(245,166,35,0.13); }
.role-pill-text { font-size: 10px; font-weight: 700; color: var(--ds-warning); }
.nav-placeholder { width: 36px; flex-shrink: 0; }

.quick-panel { background: var(--ds-surface); padding: 12px 16px 10px; border-bottom: 1px solid var(--ds-hairline); flex-shrink: 0; }
.quick-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; gap: 10px; }
.quick-title { font-size: 13px; font-weight: 700; color: var(--ds-ink-1); }
.quick-tip { font-size: 11px; color: var(--ds-ink-4); }
.quick-scroll { white-space: nowrap; }
.quick-track { display: inline-flex; gap: 8px; padding-bottom: 2px; }
.quick-chip { background: var(--ds-brand-soft); border-radius: var(--ds-r-pill); padding: 8px 14px; transition: opacity 0.18s; }
.chip-pressed { opacity: 0.7; }
.quick-chip-text { font-size: 12px; color: var(--ds-brand); font-weight: 600; }

.messages-area { flex: 1; padding: 14px 20px 14px 16px; overflow-y: auto; box-sizing: border-box; }
.loading-block { display: flex; flex-direction: column; align-items: center; padding: 50px 0; gap: 14px; }
.loading-text { font-size: 13px; color: var(--ds-ink-3); }
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 70px 20px; gap: 8px; }
.empty-ico { width: 80px; height: 80px; border-radius: 24px; background: var(--ds-surface); display: flex; align-items: center; justify-content: center; box-shadow: var(--ds-shadow-sm); margin-bottom: 8px; }
.empty-text { font-size: 16px; font-weight: 700; color: var(--ds-ink-2); }
.empty-desc { font-size: 13px; color: var(--ds-ink-4); }

.msg-list { display: flex; flex-direction: column; gap: 16px; padding-bottom: 8px; }
.msg-item { display: flex; gap: 10px; animation: fadeIn 0.25s var(--ds-ease); }
.msg-item.mine { flex-direction: row-reverse; padding-left: 50px; padding-right: 8px; }
.msg-item.other { padding-right: 50px; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.msg-avatar { width: 36px; height: 36px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;  }
.msg-item.other .msg-avatar { background: var(--ds-grad-brand); }
.msg-item.mine .msg-avatar { background: var(--ds-grad-cyan);  }
.avatar-text { color: #fff; font-size: 14px; font-weight: 800; }

.msg-bubble-wrap { max-width: 70%; min-width: 0; flex-shrink: 1; }
.msg-info { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }
.msg-item.mine .msg-info { flex-direction: row-reverse; }
.sender-name { font-size: 11px; color: var(--ds-ink-3); font-weight: 600; }
.msg-time { font-size: 10px; color: var(--ds-ink-4); letter-spacing: 0.3px; }

.msg-bubble { padding: 11px 14px; border-radius: 14px; word-break: break-word; overflow-wrap: anywhere; }
.msg-item.other .msg-bubble { background: var(--ds-surface); border-bottom-left-radius: 4px; border: 1px solid var(--ds-hairline); }
.msg-item.mine .msg-bubble { background: var(--ds-grad-brand); border-bottom-right-radius: 4px; box-shadow: var(--ds-shadow-brand); }
.msg-text { font-size: 14px; line-height: 1.5; }
.msg-item.other .msg-text { color: var(--ds-ink-1); }
.msg-item.mine .msg-text { color: #fff; }

.input-bar { display: flex; gap: 10px; padding: 10px 16px; padding-bottom: calc(10px + env(safe-area-inset-bottom)); background: var(--ds-surface); border-top: 1px solid var(--ds-hairline); flex-shrink: 0; }
.input-wrap { flex: 1; display: flex; align-items: center; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 0 14px; min-height: 38px; }
.msg-input { flex: 1; font-size: 15px; color: var(--ds-ink-1); background: transparent; border: none; height: 38px; }
.ph { color: var(--ds-ink-4); }
.send-btn { width: 38px; height: 38px; border-radius: 12px; background: var(--ds-bg-sunken); display: flex; align-items: center; justify-content: center; transition: all 0.18s var(--ds-ease); }
.send-btn.active { background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); }
.send-pressed { transform: scale(0.92); }
</style>
