<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack" hover-class="back-pressed">
					<text class="back-char">‹</text>
				</view>
				<text class="nav-title">AI 医疗助手</text>
				<view class="nav-menu" @click="showMenu">
					<text class="menu-text">•••</text>
				</view>
			</view>
		</view>

		<view class="messages-area">
			<!-- 欢迎 -->
			<view class="welcome-card" v-if="showWelcome">
				<view class="welcome-icon-box">
					<text class="welcome-icon-letter">AI</text>
				</view>
				<text class="welcome-title">您好！我是 AI 医疗助手</text>
				<text class="welcome-desc">我可以为您提供：</text>
				<view class="feature-row">
					<view class="feature-pill" v-for="t in ['疾病咨询','报告解读','健康建议']" :key="t">
						<text class="feature-text">{{ t }}</text>
					</view>
				</view>
			</view>

			<!-- 消息 -->
			<view class="msg-list">
				<view class="msg-item" v-for="(msg, i) in messages" :key="msg.id" :style="{ animationDelay: i * 0.06 + 's' }">
					<view class="msg-row ai-row" v-if="msg.message_type === 'assistant'">
						<view class="avatar ai-avatar"><text class="avatar-letter">AI</text></view>
						<view class="bubble ai-bubble">
							<text class="bubble-text">{{ msg.content }}</text>
							<text class="msg-time">{{ formatTime(msg.timestamp) }}</text>
						</view>
					</view>
					<view class="msg-row user-row" v-else>
						<view class="bubble user-bubble">
							<text class="bubble-text">{{ msg.content }}</text>
							<text class="msg-time">{{ formatTime(msg.timestamp) }}</text>
						</view>
					</view>
				</view>

				<view class="typing-row" v-if="isTyping">
					<view class="avatar ai-avatar"><text class="avatar-letter">AI</text></view>
					<view class="typing-bubble">
						<view class="typing-dot"></view>
						<view class="typing-dot"></view>
						<view class="typing-dot"></view>
					</view>
				</view>
			</view>
			<view style="height: 160px;"></view>
		</view>

		<!-- 快捷问题 -->
		<view class="quick-area" v-if="showWelcome">
			<scroll-view scroll-x show-scrollbar="false" class="quick-scroll">
				<view class="quick-chip" v-for="q in quickQuestions" :key="q" @click="sendQuickQuestion(q)" hover-class="chip-pressed">
					<text class="quick-text">{{ q }}</text>
				</view>
			</scroll-view>
		</view>

		<!-- 输入栏 -->
		<view class="input-bar">
			<view class="input-wrap">
				<input class="msg-input" v-model="inputMessage" placeholder="输入您的问题..." placeholder-class="input-ph" :adjust-position="true" @confirm="sendMessage" />
			</view>
			<view class="send-btn" :class="{ active: inputMessage.trim() && !isTyping }" @click="sendMessage" hover-class="send-pressed">
				<text class="send-arrow">↑</text>
			</view>
		</view>

		<bottom-nav-doctor v-if="userType === 'doctor'" current="chat"></bottom-nav-doctor>
		<bottom-nav-family v-else-if="userType === 'family'" current="chat-ai"></bottom-nav-family>
		<bottom-nav-patient v-else current="chat"></bottom-nav-patient>
	</view>
</template>

<script>
import { mlAPI } from '@/utils/request.js'
import BottomNavDoctor from '@/components/bottom_nav/BottomNavDoctor.vue'
import BottomNavPatient from '@/components/bottom_nav/BottomNavPatient.vue'
import BottomNavFamily from '@/components/bottom_nav/BottomNavFamily.vue'

export default {
	components: { BottomNavDoctor, BottomNavPatient, BottomNavFamily },
	data() {
		return {
			userType: 'patient', messages: [], inputMessage: '', isTyping: false, scrollTop: 0,
			userInfo: {}, showWelcome: true,
			quickQuestions: ['脑瘤有哪些症状？', '如何解读MRI报告？', '治疗方案有哪些？', '日常注意事项']
		}
	},
	onLoad(options) {
		if (options?.userType) this.userType = options.userType
		else { const c = uni.getStorageSync('userType'); if (c) this.userType = c }
		this.userInfo = uni.getStorageSync('user') || {}
		this.addWelcomeMessage()
	},
	methods: {
		goBack() { uni.navigateBack({ delta: 1, fail: () => { uni.reLaunch({ url: '/pages/homePatient/homePatient' }) } }) },
		async sendMessageStreamH5() { return false },
		addWelcomeMessage() {
			setTimeout(() => {
				this.showWelcome = false
				this.messages.push({ message_type: 'assistant', content: '您好！我是AI医疗助手，专注于脑瘤相关问题。有什么可以帮助您的吗？', timestamp: new Date(), id: Date.now() })
				this.scrollToBottom()
			}, 3000)
		},
		async sendMessage() {
			if (!this.inputMessage.trim() || this.isTyping) return
			this.showWelcome = false
			const message = this.inputMessage.trim(); this.inputMessage = ''
			this.messages.push({ message_type: 'user', content: message, timestamp: new Date(), id: Date.now() })
			this.scrollToBottom(); this.isTyping = true
			try {
				const apiMessages = this.messages.map(m => ({ role: m.message_type === 'user' ? 'user' : 'assistant', content: m.content }))
				let streamed = false
				if (typeof window !== 'undefined' && typeof fetch === 'function') { try { streamed = await this.sendMessageStreamH5(apiMessages) } catch(e) {} }
				if (!streamed) {
					const resp = await mlAPI.chat({ messages: apiMessages, patient_info: this.userInfo })
					if (resp.success) this.messages.push({ message_type: 'assistant', content: resp.response, timestamp: new Date(), id: Date.now() })
					else throw new Error(resp.response || resp.error || 'AI服务暂不可用')
				}
			} catch(e) {
				const errMsg = e.message || '未知错误'; this.messages.push({ message_type: 'assistant', content: '抱歉，' + errMsg + '。请稍后再试。', timestamp: new Date(), id: Date.now() })
			} finally { this.isTyping = false; this.scrollToBottom() }
		},
		sendQuickQuestion(q) { this.showWelcome = false; this.inputMessage = q; this.sendMessage() },
		scrollToBottom() { this.$nextTick(() => { this.scrollTop = 999999 }) },
		formatTime(ts) { const d = new Date(ts); return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}` },
		showMenu() { uni.showActionSheet({ itemList: ['清空聊天记录'], success: r => { if (r.tapIndex === 0) this.clearChat() } }) },
		clearChat() { uni.showModal({ title: '确认清空', content: '确定要清空所有聊天记录吗？', success: r => { if (r.confirm) { this.messages = []; this.addWelcomeMessage() } } }) }
	}
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: var(--ds-bg); font-family: var(--ds-font); }

.navbar { position: sticky; top: 0; z-index: 100; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; display: flex; align-items: center; justify-content: space-between; padding: 52px 16px 12px; }
.nav-title { font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-back { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
.back-pressed { background: var(--ds-brand-ghost); }
.back-char { font-size: 32px; font-weight: 300; color: var(--ds-brand); line-height: 1; margin-top: -4px; }
.nav-menu { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
.menu-text { font-size: 16px; color: var(--ds-brand); letter-spacing: 2px; }
.nav-placeholder { width: 36px; }

.messages-area { flex: 1; padding: 16px; overflow-y: auto; }

.welcome-card { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 28px 20px; text-align: center; margin-bottom: 16px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.welcome-icon-box { width: 56px; height: 56px; border-radius: 16px; background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.welcome-icon-letter { font-size: 18px; font-weight: 800; color: #fff; letter-spacing: 0.5px; }
.welcome-title { display: block; font-size: 20px; font-weight: 800; color: var(--ds-ink-1); margin-bottom: 8px; }
.welcome-desc { display: block; font-size: 14px; color: var(--ds-ink-3); margin-bottom: 14px; }
.feature-row { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
.feature-pill { padding: 6px 14px; border-radius: var(--ds-r-pill); background: var(--ds-brand-soft); }
.feature-text { font-size: 13px; color: var(--ds-brand); font-weight: 600; }

.msg-list { display: flex; flex-direction: column; gap: 12px; }
.msg-item { animation: slideIn 0.25s var(--ds-ease); }
.msg-row { display: flex; gap: 8px; max-width: 82%; }
.ai-row { align-self: flex-start; }
.user-row { align-self: flex-end; flex-direction: row-reverse; }

.avatar { width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ai-avatar { background: var(--ds-grad-brand);  }
.avatar-letter { font-size: 11px; font-weight: 800; color: #fff; letter-spacing: 0.3px; }

.bubble { padding: 11px 14px; border-radius: 16px; }
.ai-bubble { background: var(--ds-surface); border-bottom-left-radius: 4px; border: 1px solid var(--ds-hairline); }
.user-bubble { background: var(--ds-grad-brand); border-bottom-right-radius: 4px; box-shadow: var(--ds-shadow-brand); }
.bubble-text { font-size: 15px; line-height: 1.5; display: block; }
.ai-bubble .bubble-text { color: var(--ds-ink-1); }
.user-bubble .bubble-text { color: #fff; }
.msg-time { display: block; font-size: 10px; margin-top: 4px; text-align: right; font-family: var(--ds-font-mono); letter-spacing: 0.3px; }
.ai-bubble .msg-time { color: var(--ds-ink-4); }
.user-bubble .msg-time { color: rgba(255,255,255,0.7); }

.typing-row { display: flex; gap: 8px; align-items: flex-end; }
.typing-bubble { display: flex; gap: 4px; background: var(--ds-surface); border-radius: 16px; padding: 12px 16px; border: 1px solid var(--ds-hairline); }
.typing-dot { width: 7px; height: 7px; background: var(--ds-ink-4); border-radius: 50%; animation: bounce 1.4s infinite ease-in-out; }
.typing-dot:nth-child(2) { animation-delay: 0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0.32s; }

.quick-area { padding: 0 0 8px; }
.quick-scroll { white-space: nowrap; padding: 0 16px; }
.quick-scroll::-webkit-scrollbar { display: none; }
.quick-chip { display: inline-block; padding: 8px 16px; border-radius: var(--ds-r-pill); background: var(--ds-surface); border: 1px solid var(--ds-hairline); margin-right: 8px; transition: background 0.15s; box-shadow: var(--ds-shadow-sm); }
.chip-pressed { background: var(--ds-brand-soft); }
.quick-text { font-size: 13px; color: var(--ds-brand); font-weight: 600; }

.input-bar { display: flex; gap: 10px; padding: 10px 16px 70px; background: var(--ds-surface); border-top: 1px solid var(--ds-hairline); }
.input-wrap { flex: 1; display: flex; align-items: center; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 0 14px; min-height: 38px; }
.msg-input { flex: 1; font-size: 15px; color: var(--ds-ink-1); background: transparent; border: none; height: 38px; }
.input-ph { color: var(--ds-ink-4); }
.send-btn { width: 38px; height: 38px; border-radius: 12px; background: var(--ds-bg-sunken); display: flex; align-items: center; justify-content: center; transition: all 0.18s var(--ds-ease); }
.send-btn.active { background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); }
.send-pressed { transform: scale(0.92); }
.send-arrow { font-size: 18px; font-weight: 700; color: #fff; }

@keyframes slideIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce { 0%,80%,100% { transform: scale(0); } 40% { transform: scale(1); } }
</style>
