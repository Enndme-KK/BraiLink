<template>
	<view class="page">
		<view class="hero ds-scanline ds-grid-bg">
			<view class="hero-glow"></view>
			<view class="hero-inner">
				<view class="user-row ds-rise ds-d1">
					<view class="avatar-box">
						<view class="avatar-circle">
							<text class="avatar-text">{{ avatarText }}</text>
						</view>
						<view class="avatar-tag"><text class="avatar-tag-text">家属</text></view>
					</view>
					<view class="user-info">
						<text class="user-name">{{ displayName }}</text>
						<text class="user-id ds-mono">@{{ userInfo.username || 'family' }}</text>
						<view class="user-tags">
							<view class="tag-pill"><text class="tag-text">{{ profile.phone || userInfo.phone || '手机号未填写' }}</text></view>
						</view>
					</view>
				</view>
			</view>
		</view>

		<view class="content">
			<!-- 绑定卡 -->
			<view class="bound-card ds-rise ds-d2">
				<view class="section-row">
					<view>
						<text class="section-label">绑定患者</text>
						<text class="section-hint ds-mono">BOUND PATIENT</text>
					</view>
					<view class="manage-btn" @click="goBindPage" hover-class="btn-pressed">
						<text>{{ boundPatient ? '管理' : '去绑定' }}</text>
					</view>
				</view>

				<view class="patient-mini" v-if="boundPatient">
					<view class="mini-avatar"><text>{{ getAvatarText(boundPatient.name) }}</text></view>
					<view class="mini-info">
						<text class="mini-name">{{ boundPatient.name }}</text>
						<text class="mini-desc">{{ boundPatient.relationship || '家属' }} · {{ boundPatient.age || '年龄待完善' }}岁</text>
					</view>
					<view class="mini-status" @click.stop="unbindCurrentPatient">
						<text>{{ unbinding ? '处理中' : '解绑' }}</text>
					</view>
				</view>

				<view class="empty-bound" v-else>
					<view class="empty-ico">
						<svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#A2A9BC" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 13a4 4 0 0 0 5.6.5l3-3A4 4 0 0 0 11.9 5l-1.2 1.1"/><path d="M15 11a4 4 0 0 0-5.6-.5l-3 3A4 4 0 0 0 12.1 19l1.2-1.1"/></svg>
					</view>
					<text class="empty-text">还没有绑定患者</text>
					<text class="empty-desc">绑定后可查看病历摘要并联系相关医生</text>
				</view>
			</view>

			<!-- 设置 -->
			<view class="section-head">
				<text class="section-label">设置与服务</text>
				<text class="section-hint ds-mono">SETTINGS · SERVICES</text>
			</view>
			<view class="list-group ds-rise ds-d3">
				<view class="list-item" v-for="(item, index) in settings" :key="item.key" @click="handleSetting(item)" hover-class="item-pressed">
					<view class="item-ico" :style="{ background: getIconBg(index) }">
						<view v-html="item.svg"></view>
					</view>
					<view class="item-body">
						<text class="item-title">{{ item.name }}</text>
						<text class="item-desc">{{ item.desc }}</text>
					</view>
					<view class="item-chevron"><text class="chevron-char">›</text></view>
				</view>
			</view>

			<view class="logout-area ds-rise ds-d4">
				<view class="logout-btn" @click="logout" hover-class="btn-pressed">
					<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#FF4D5E" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5M21 12H9"/></svg>
					<text class="logout-text">退出登录</text>
				</view>
			</view>
			<view style="height: 80px;"></view>
		</view>

		<bottom-nav-family current="profile" />
	</view>
</template>

<script>
import { authAPI, familyAPI } from '@/utils/request.js'
import { clearLoginInfo, getCurrentUser, requireAuth, getCurrentUserType } from '@/utils/auth.js'
import BottomNavFamily from '@/components/bottom_nav/BottomNavFamily.vue'

const SVG = {
	bind: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 13a4 4 0 0 0 5.6.5l3-3A4 4 0 0 0 11.9 5l-1.2 1.1"/><path d="M15 11a4 4 0 0 0-5.6-.5l-3 3A4 4 0 0 0 12.1 19l1.2-1.1"/></svg>',
	chat: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 20l1-4a8.5 8.5 0 0 1-1-4 8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5z"/></svg>',
	account: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M5 21v-1a7 7 0 0 1 14 0v1"/></svg>',
	notice: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 16v-5a6 6 0 0 0-12 0v5l-2 2v1h16v-1l-2-2z"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>',
	about: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'
}

export default {
	name: 'FamilyProfile',
	components: { BottomNavFamily },
	data() {
		return {
			profile: {}, boundPatient: null, userInfo: {}, unbinding: false,
			settings: [
				{ key: 'bind', svg: SVG.bind, name: '绑定管理', desc: '添加、查看或解除患者绑定' },
				{ key: 'chat', svg: SVG.chat, name: '医生沟通', desc: '查看与患者相关的医生' },
				{ key: 'account', svg: SVG.account, name: '账号管理', desc: '修改基础账号信息' },
				{ key: 'about', svg: SVG.about, name: '关于我们', desc: '软件版本与说明' }
			]
		}
	},
	computed: {
		displayName() { return this.profile.name || this.userInfo.name || this.userInfo.username || '家属用户' },
		avatarText() { return this.getAvatarText(this.displayName) }
	},
	onLoad() {
		if (!requireAuth()) return
		if (!this.ensureFamilyUser()) return
		this.loadProfile()
	},
	onShow() {
		if (!requireAuth()) return
		if (!this.ensureFamilyUser()) return
		this.loadProfile()
	},
	methods: {
		ensureFamilyUser() {
			if (getCurrentUserType() !== 'family') {
				uni.showToast({ title: '仅家属可访问', icon: 'none' })
				uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' })
				return false
			}
			this.userInfo = getCurrentUser() || {}
			return true
		},
		async loadProfile() {
			try {
				const [profile, summary] = await Promise.all([familyAPI.getMyProfile(), familyAPI.getHomeSummary()])
				this.profile = profile || {}
				this.boundPatient = summary && summary.bound ? summary.patient : null
			} catch (error) {
				const message = error?.response?.data?.error || error?.message || '加载失败'
				uni.showToast({ title: message, icon: 'none' })
			}
		},
		getAvatarText(name) { return name ? String(name).slice(0, 1) : '家' },
		getIconBg(i) {
			const list = [
				'linear-gradient(135deg, #00C2D7 0%, #1FB877 100%)',
				'linear-gradient(135deg, #0A5CFF 0%, #00C2D7 100%)',
				'linear-gradient(135deg, #0A5CFF 0%, #0742C4 100%)',
				'linear-gradient(135deg, #F5A623 0%, #FF7A59 100%)',
				'linear-gradient(135deg, #69728C 0%, #2B3658 100%)'
			]
			return list[i] || list[4]
		},
		handleSetting(item) {
			const routes = {
				bind: '/pages/family/bind',
				chat: '/pages/family/chat-list',
				account: '/pages/settings/account/account',
				notice: '/pages/settings/sysNotice/sysNotice',
				about: '/pages/settings/about/about'
			}
			const url = routes[item.key]
			if (!url) return
			if (item.key === 'bind' || item.key === 'chat') uni.reLaunch({ url })
			else uni.navigateTo({ url })
		},
		goBindPage() { uni.navigateTo({ url: '/pages/family/bind' }) },
		unbindCurrentPatient() {
			if (!this.boundPatient || !this.boundPatient.binding_id || this.unbinding) {
				this.goBindPage(); return
			}
			uni.showModal({
				title: '确认解绑',
				content: `确定解除与"${this.boundPatient.name || '该患者'}"的绑定关系吗？`,
				confirmText: '解绑', cancelText: '取消',
				success: async (res) => {
					if (!res.confirm) return
					this.unbinding = true
					try {
						uni.showLoading({ title: '解绑中...', mask: true })
						const response = await familyAPI.unbindPatient({ binding_id: this.boundPatient.binding_id })
						uni.hideLoading()
						this.boundPatient = null
						uni.showToast({ title: response.message || '解绑成功', icon: 'success' })
						this.loadProfile()
					} catch (error) {
						uni.hideLoading()
						uni.showToast({ title: error.response?.data?.error || error.message || '解绑失败', icon: 'none' })
					} finally { this.unbinding = false }
				}
			})
		},
		logout() {
			uni.showModal({
				title: '确认退出', content: '退出后需要重新登录家属端账号',
				confirmText: '退出', cancelText: '取消',
				success: async (res) => {
					if (!res.confirm) return
					try { await authAPI.logout() } catch (e) {}
					clearLoginInfo()
					uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' })
				}
			})
		}
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); font-family: var(--ds-font); padding-bottom: 90px; }

.hero { --ds-scan-h: 200px; position: relative; padding: 78px 24px 32px; background: linear-gradient(160deg, #0C1733 0%, #0A3A8C 55%, #0A5CFF 130%); overflow: hidden; }
.hero-glow { position: absolute; top: -60px; right: -60px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(0,194,215,0.45) 0%, transparent 70%); filter: blur(8px); }
.hero-inner { position: relative; }
.user-row { display: flex; gap: 16px; align-items: center; }
.avatar-box { position: relative; flex-shrink: 0; }
.avatar-circle { width: 80px; height: 80px; border-radius: 22px; background: var(--ds-grad-cyan); border: 2px solid rgba(255,255,255,0.25); display: flex; align-items: center; justify-content: center;  }
.avatar-text { color: #fff; font-size: 32px; font-weight: 800; }
.avatar-tag { position: absolute; bottom: -6px; right: -6px; padding: 3px 9px; border-radius: var(--ds-r-pill); background: var(--ds-cyan); border: 1.5px solid #0A3A8C; }
.avatar-tag-text { font-size: 10px; font-weight: 800; color: #fff; letter-spacing: 0.3px; }
.user-info { flex: 1; min-width: 0; color: #fff; }
.user-name { display: block; font-size: 22px; font-weight: 800; color: #fff; margin-bottom: 4px; }
.user-id { display: block; font-size: 12px; color: rgba(255,255,255,0.7); margin-bottom: 8px; }
.user-tags { display: flex; gap: 6px; }
.tag-pill { padding: 3px 9px; border-radius: var(--ds-r-pill); background: rgba(255,255,255,0.13); border: 1px solid rgba(255,255,255,0.18); }
.tag-text { font-size: 11px; font-weight: 600; color: #fff; }

.content { padding: 20px 20px 0; }

.bound-card { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 18px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); margin-bottom: 18px; }
.section-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 14px; }
.section-label { display: block; font-size: 16px; font-weight: 800; color: var(--ds-ink-1); }
.section-hint { display: block; margin-top: 4px; font-size: 10px; font-weight: 600; color: var(--ds-ink-4); letter-spacing: 1px; }
.manage-btn { padding: 6px 14px; border-radius: var(--ds-r-pill); background: var(--ds-brand-soft); flex-shrink: 0; transition: background 0.15s; }
.manage-btn text { font-size: 12px; font-weight: 700; color: var(--ds-brand); }
.btn-pressed { opacity: 0.8; }

.patient-mini { display: flex; align-items: center; gap: 12px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 12px; }
.mini-avatar { width: 44px; height: 44px; border-radius: 14px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; flex-shrink: 0;  }
.mini-avatar text { color: #fff; font-size: 18px; font-weight: 800; }
.mini-info { flex: 1; min-width: 0; }
.mini-name { display: block; font-size: 15px; font-weight: 700; color: var(--ds-ink-1); }
.mini-desc { display: block; margin-top: 3px; font-size: 11px; color: var(--ds-ink-3); }
.mini-status { padding: 5px 11px; border-radius: var(--ds-r-pill); background: rgba(255,77,94,0.13); flex-shrink: 0; }
.mini-status text { font-size: 11px; font-weight: 700; color: var(--ds-danger); }

.empty-bound { text-align: center; padding: 22px 10px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); }
.empty-ico { width: 52px; height: 52px; border-radius: 50%; background: var(--ds-surface); display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; }
.empty-text { display: block; font-size: 14px; font-weight: 700; color: var(--ds-ink-2); margin-bottom: 4px; }
.empty-desc { display: block; font-size: 11px; color: var(--ds-ink-4); line-height: 1.55; }

.section-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 10px; padding: 0 4px; }

.list-group { background: var(--ds-surface); border-radius: var(--ds-r-md); overflow: hidden; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.list-item { display: flex; align-items: center; padding: 14px 16px; gap: 14px; transition: background 0.15s; }
.list-item + .list-item { border-top: 1px solid var(--ds-hairline); }
.item-pressed { background: var(--ds-bg-sunken); }
.item-ico { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 12px rgba(10,92,255,0.18); }
.item-body { flex: 1; min-width: 0; }
.item-title { display: block; font-size: 15px; font-weight: 600; color: var(--ds-ink-1); margin-bottom: 2px; }
.item-desc { display: block; font-size: 11px; color: var(--ds-ink-3); }
.item-chevron { flex-shrink: 0; }
.chevron-char { font-size: 22px; font-weight: 300; color: var(--ds-ink-4); }

.logout-area { padding: 18px 0 0; }
.logout-btn { background: var(--ds-surface); border: 1px solid var(--ds-hairline); border-radius: var(--ds-r-sm); padding: 14px; display: flex; align-items: center; justify-content: center; gap: 8px; transition: background 0.15s; }
.logout-text { font-size: 16px; font-weight: 600; color: var(--ds-danger); }
</style>
