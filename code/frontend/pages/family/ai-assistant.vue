<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<text class="nav-title">AI 护理助手</text>
				<view class="clear-btn" @click="clearChat" hover-class="back-pressed">
					<text class="clear-text">清空</text>
				</view>
			</view>
		</view>

		<scroll-view class="messages-scroll" scroll-y="true" :scroll-top="scrollTop" :scroll-with-animation="true">
			<view class="welcome-card ds-rise ds-d1" v-if="showWelcome">
				<view class="welcome-icon-box">
					<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 8V4.5M12 4.5h-1.5M12 4.5h1.5"/><circle cx="9" cy="13.5" r="1.1" fill="#fff" stroke="none"/><circle cx="15" cy="13.5" r="1.1" fill="#fff" stroke="none"/><path d="M2 12.5v3M22 12.5v3"/></svg>
				</view>
				<text class="welcome-title">家庭护理建议助手</text>
				<text class="welcome-desc">可咨询日常照护、营养饮食、情绪陪伴和复诊准备等问题。涉及病情变化时，请以医生意见为准。</text>
				<view class="feature-row">
					<view class="feature-pill" v-for="t in ['日常护理','营养饮食','心理支持']" :key="t">
						<text class="feature-text">{{ t }}</text>
					</view>
				</view>
			</view>

			<view class="message-list">
				<view class="msg-item" v-for="message in messages" :key="message.id" :class="message.message_type">
					<view class="msg-row" :class="message.message_type === 'assistant' ? 'ai-row' : 'user-row'">
						<view class="avatar ai-avatar" v-if="message.message_type === 'assistant'"><text class="avatar-letter">AI</text></view>
						<view class="bubble" :class="message.message_type === 'assistant' ? 'ai-bubble' : 'user-bubble'">
							<text class="bubble-text">{{ message.content }}</text>
							<text class="msg-time ds-mono">{{ formatTime(message.timestamp) }}</text>
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
			<view style="height: 16px;"></view>
		</scroll-view>

		<view class="quick-area" v-if="showWelcome && quickQuestions.length">
			<scroll-view scroll-x show-scrollbar="false" class="quick-scroll">
				<view class="quick-chip" v-for="(q, i) in quickQuestions" :key="i" @click="sendQuickQuestion(q)" hover-class="chip-pressed">
					<text class="quick-text">{{ q }}</text>
				</view>
			</scroll-view>
		</view>

		<view class="input-bar">
			<view class="input-wrap">
				<input class="msg-input" v-model="inputMessage" placeholder="输入想咨询的问题..." placeholder-class="input-ph" :adjust-position="true" @confirm="sendMessage" />
			</view>
			<view class="send-btn" :class="{ active: inputMessage.trim() && !isTyping }" @click="sendMessage" hover-class="send-pressed">
				<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2 11 13"/><path d="M22 2l-7 20-4-9-9-4z"/></svg>
			</view>
		</view>

		<bottom-nav-family current="ai" />
	</view>
</template>

<script>
import BottomNavFamily from '@/components/bottom_nav/BottomNavFamily.vue'
import { mlAPI } from '@/utils/request.js'
import { requireAuth, getCurrentUserType } from '@/utils/auth.js'

const WELCOME_MESSAGE = '您好，我是您的专属家庭护理助手。可以向我询问关于患者日常照顾、营养饮食或康复注意事项的任何问题。'
const FALLBACK_MESSAGE = '抱歉，我暂时没能回答这个问题。可以稍后重试；如果涉及检查结果或病情变化，请及时联系医生。'

export default {
	name: 'FamilyAiAssistant',
	components: { BottomNavFamily },
	data() {
		return {
			messages: [], inputMessage: '', isTyping: false, scrollTop: 0, showWelcome: true,
			quickQuestions: ['术后在家要注意什么？', '患者没胃口时饮食怎么安排？', '家属如何帮助患者缓解焦虑？', '复诊前需要准备哪些资料？']
		}
	},
	onLoad() { if (!this.ensureFamilyAccess()) return; this.initializeChat() },
	onShow() { this.ensureFamilyAccess() },
	methods: {
		ensureFamilyAccess() {
			if (!requireAuth()) return false
			if (getCurrentUserType() !== 'family') {
				uni.showToast({ title: '仅家属可访问', icon: 'none' })
				setTimeout(() => uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' }), 1200)
				return false
			}
			return true
		},
		initializeChat() {
			if (this.messages.length > 0) return
			this.messages = [this.createAssistantMessage(WELCOME_MESSAGE)]
			this.scrollToBottom()
		},
		clearChat() {
			this.messages = [this.createAssistantMessage(WELCOME_MESSAGE)]
			this.inputMessage = ''; this.isTyping = false; this.showWelcome = true
			this.scrollToBottom()
		},
		createAssistantMessage(content) { return { id: Date.now() + Math.random(), message_type: 'assistant', content, timestamp: new Date() } },
		createUserMessage(content) { return { id: Date.now() + Math.random(), message_type: 'user', content, timestamp: new Date() } },
		buildApiMessages() { return this.messages.map(m => ({ role: m.message_type === 'user' ? 'user' : 'assistant', content: m.content })) },
		async sendMessage() {
			if (!this.ensureFamilyAccess()) return
			if (!this.inputMessage.trim() || this.isTyping) return
			const message = this.inputMessage.trim()
			this.inputMessage = ''; this.showWelcome = false
			this.messages.push(this.createUserMessage(message))
			this.scrollToBottom(); this.isTyping = true
			try {
				const r = await mlAPI.chat({ messages: this.buildApiMessages() })
				if (r && r.success && r.response) this.messages.push(this.createAssistantMessage(r.response))
				else throw new Error(r?.response || 'AI 服务暂时不可用')
			} catch (e) {
				this.messages.push(this.createAssistantMessage(FALLBACK_MESSAGE))
			} finally { this.isTyping = false; this.scrollToBottom() }
		},
		sendQuickQuestion(q) { if (!this.ensureFamilyAccess()) return; this.inputMessage = q; this.sendMessage() },
		scrollToBottom() { this.$nextTick(() => { this.scrollTop = 0; setTimeout(() => { this.scrollTop = 999999 }, 30) }) },
		formatTime(ts) { const d = new Date(ts); return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}` }
	}
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: var(--ds-bg); font-family: var(--ds-font); padding-bottom: calc(60px + env(safe-area-inset-bottom)); }

.navbar { position: sticky; top: 0; z-index: 100; flex-shrink: 0; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; display: flex; align-items: center; justify-content: space-between; padding: 52px 16px 12px; }
.nav-title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); flex: 1; text-align: center; }
.clear-btn { position: absolute; right: 16px; top: 50px; padding: 6px 12px; border-radius: var(--ds-r-pill); background: var(--ds-bg-sunken); }
.back-pressed { opacity: 0.7; }
.clear-text { font-size: 12px; font-weight: 600; color: var(--ds-ink-3); }

.messages-scroll { flex: 1; padding: 16px; box-sizing: border-box; }

.welcome-card { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 28px 20px; text-align: center; margin-bottom: 16px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.welcome-icon-box { width: 56px; height: 56px; border-radius: 16px; background: var(--ds-grad-cyan);  display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.welcome-title { display: block; font-size: 19px; font-weight: 800; color: var(--ds-ink-1); margin-bottom: 8px; }
.welcome-desc { display: block; font-size: 13px; line-height: 1.65; color: var(--ds-ink-3); margin-bottom: 14px; }
.feature-row { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
.feature-pill { padding: 6px 12px; border-radius: var(--ds-r-pill); background: var(--ds-cyan-soft); }
.feature-text { font-size: 12px; color: #008695; font-weight: 700; }

.message-list { display: flex; flex-direction: column; gap: 12px; }
.msg-item { animation: slideIn 0.25s var(--ds-ease); }
.msg-row { display: flex; gap: 8px; max-width: 82%; }
.ai-row { align-self: flex-start; }
.user-row { align-self: flex-end; flex-direction: row-reverse; margin-left: auto; }

.avatar { width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ai-avatar { background: var(--ds-grad-cyan);  }
.avatar-letter { font-size: 11px; font-weight: 800; color: #fff; }

.bubble { padding: 11px 14px; border-radius: 16px; }
.ai-bubble { background: var(--ds-surface); border-bottom-left-radius: 4px; border: 1px solid var(--ds-hairline); }
.user-bubble { background: var(--ds-grad-brand); border-bottom-right-radius: 4px; box-shadow: var(--ds-shadow-brand); }
.bubble-text { font-size: 14px; line-height: 1.55; display: block; white-space: pre-wrap; word-break: break-word; }
.ai-bubble .bubble-text { color: var(--ds-ink-1); }
.user-bubble .bubble-text { color: #fff; }
.msg-time { display: block; font-size: 10px; margin-top: 4px; text-align: right; letter-spacing: 0.3px; }
.ai-bubble .msg-time { color: var(--ds-ink-4); }
.user-bubble .msg-time { color: rgba(255,255,255,0.7); }

.typing-row { display: flex; gap: 8px; align-items: flex-end; }
.typing-bubble { display: flex; gap: 4px; background: var(--ds-surface); border-radius: 16px; padding: 12px 16px; border: 1px solid var(--ds-hairline); }
.typing-dot { width: 7px; height: 7px; background: var(--ds-ink-4); border-radius: 50%; animation: bounce 1.4s infinite ease-in-out; }
.typing-dot:nth-child(2) { animation-delay: 0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0.32s; }

.quick-area { padding: 4px 0 8px; flex-shrink: 0; }
.quick-scroll { white-space: nowrap; padding: 0 16px; }
.quick-scroll::-webkit-scrollbar { display: none; }
.quick-chip { display: inline-block; padding: 8px 14px; border-radius: var(--ds-r-pill); background: var(--ds-surface); border: 1px solid var(--ds-hairline); margin-right: 8px; box-shadow: var(--ds-shadow-sm); }
.chip-pressed { background: var(--ds-brand-soft); }
.quick-text { font-size: 13px; color: var(--ds-brand); font-weight: 600; }

.input-bar { display: flex; gap: 10px; padding: 10px 16px; background: var(--ds-surface); border-top: 1px solid var(--ds-hairline); flex-shrink: 0; }
.input-wrap { flex: 1; display: flex; align-items: center; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 0 14px; min-height: 38px; }
.msg-input { flex: 1; font-size: 15px; color: var(--ds-ink-1); background: transparent; border: none; height: 38px; }
.input-ph { color: var(--ds-ink-4); }
.send-btn { width: 38px; height: 38px; border-radius: 12px; background: var(--ds-bg-sunken); display: flex; align-items: center; justify-content: center; transition: all 0.18s var(--ds-ease); }
.send-btn.active { background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); }
.send-pressed { transform: scale(0.92); }

@keyframes slideIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce { 0%,80%,100% { transform: scale(0); } 40% { transform: scale(1); } }
</style>
