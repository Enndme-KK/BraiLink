<template>
	<view class="page">
		<view class="hero ds-scanline ds-grid-bg">
			<view class="hero-glow"></view>
			<view class="hero-inner">
				<view class="user-row ds-rise ds-d1">
					<view class="avatar-box">
						<image :src="avatarUrl" class="avatar-img" mode="aspectFill"></image>
						<view class="avatar-tag"><text class="avatar-tag-text">家属</text></view>
					</view>
					<view class="user-info">
						<text class="user-name">{{ displayName }}</text>
						<text class="user-id ds-mono">@{{ user.username || 'family' }}</text>
						<view class="user-tags">
							<view class="tag-pill"><text class="tag-text">家属端</text></view>
						</view>
					</view>
				</view>
			</view>
		</view>

		<view class="content">
			<view class="section-head">
				<text class="section-label">设置与管理</text>
				<text class="section-hint ds-mono">SETTINGS · MANAGEMENT</text>
			</view>
			<view class="list-group ds-rise ds-d2">
				<view class="list-item" v-for="(setting, index) in settingList" :key="index" @click="toPage(index)" hover-class="item-pressed">
					<view class="item-ico" :style="{ background: getIconBg(index) }">
						<view v-html="getSettingSvg(index)"></view>
					</view>
					<view class="item-body">
						<text class="item-title">{{ setting }}</text>
						<text class="item-desc">{{ getSettingDesc(index) }}</text>
					</view>
					<view class="item-badge" v-if="index === 2 && unreadNotificationCount > 0">
						<text class="badge-num">{{ unreadNotificationCount > 99 ? '99+' : unreadNotificationCount }}</text>
					</view>
					<view class="item-chevron"><text class="chevron-char">›</text></view>
				</view>
			</view>

			<view class="logout-area ds-rise ds-d3">
				<view class="logout-btn" @click="logout" hover-class="btn-pressed">
					<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#FF4D5E" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5M21 12H9"/></svg>
					<text class="logout-text">退出登录</text>
				</view>
			</view>
			<view style="height: 80px;"></view>
		</view>

		<bottom-nav-family current="profile"></bottom-nav-family>
	</view>
</template>

<script>
import BottomNavFamily from '@/components/bottom_nav/BottomNavFamily.vue'
import { notificationAPI } from '@/utils/request.js'

const SETTING_SVG = {
	account: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M5 21v-1a7 7 0 0 1 14 0v1"/></svg>',
	pwd: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
	notice: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 16v-5a6 6 0 0 0-12 0v5l-2 2v1h16v-1l-2-2z"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>',
	feedback: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 20l1-4a8.5 8.5 0 0 1-1-4 8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5z"/></svg>',
	about: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'
}

export default {
	components: { BottomNavFamily },
	data() {
		return {
			user: uni.getStorageSync('user') || {},
			unreadNotificationCount: 0,
			settingList: ['账号管理', '修改密码', '意见反馈', '关于我们']
		}
	},
	computed: {
		avatarUrl() { return this.user.avatar || '../../static/resource/img1.jpg' },
		displayName() { return this.user.name || this.user.username || '家属用户' }
	},
	onLoad() { this.loadUnreadNotificationCount() },
	onShow() { this.loadUnreadNotificationCount() },
	methods: {
		toPage(index) {
			const pages = ['/pages/settings/account/account', '/pages/settings/updatePwd/updatePwd', '/pages/settings/feedback/feedback', '/pages/settings/about/about']
			if (pages[index]) uni.navigateTo({ url: pages[index] })
		},
		getSettingSvg(i) { return [SETTING_SVG.account, SETTING_SVG.pwd, SETTING_SVG.notice, SETTING_SVG.feedback, SETTING_SVG.about][i] || SETTING_SVG.about },
		getSettingDesc(i) { return ['管理个人信息', '修改登录密码', '提交您的建议', '软件版本信息'][i] || '' },
		getIconBg(i) {
			const list = [
				'linear-gradient(135deg, #0A5CFF 0%, #0742C4 100%)',
				'linear-gradient(135deg, #1FB877 0%, #00C2D7 100%)',
				'linear-gradient(135deg, #F5A623 0%, #FF7A59 100%)',
				'linear-gradient(135deg, #00C2D7 0%, #0A5CFF 100%)',
				'linear-gradient(135deg, #69728C 0%, #2B3658 100%)'
			]
			return list[i] || list[4]
		},
		async loadUnreadNotificationCount() { try { const r = await notificationAPI.getUnreadCount(); this.unreadNotificationCount = r.count || 0 } catch (e) { this.unreadNotificationCount = 0 } },
		logout() {
			uni.showModal({
				title: '确认退出', content: '确定要退出登录吗？',
				success: r => {
					if (!r.confirm) return
					Promise.all([
						import('@/utils/auth.js'),
						import('@/utils/request.js')
					]).then(async ([auth, req]) => {
						try { await req.authAPI.logout() } catch (e) {}
						auth.clearLoginInfo()
						uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' })
					})
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
.avatar-img { width: 80px; height: 80px; border-radius: 22px; border: 2px solid rgba(255,255,255,0.25);  }
.avatar-tag { position: absolute; bottom: -6px; right: -6px; padding: 3px 9px; border-radius: var(--ds-r-pill); background: var(--ds-cyan); border: 1.5px solid #0A3A8C; }
.avatar-tag-text { font-size: 10px; font-weight: 800; color: #fff; letter-spacing: 0.3px; }
.user-info { flex: 1; min-width: 0; color: #fff; }
.user-name { display: block; font-size: 22px; font-weight: 800; color: #fff; margin-bottom: 4px; }
.user-id { display: block; font-size: 12px; color: rgba(255,255,255,0.7); margin-bottom: 8px; }
.user-tags { display: flex; gap: 6px; }
.tag-pill { padding: 3px 9px; border-radius: var(--ds-r-pill); background: rgba(255,255,255,0.13); border: 1px solid rgba(255,255,255,0.18); }
.tag-text { font-size: 11px; font-weight: 600; color: #fff; }

.content { padding: 22px 20px 0; }
.section-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 12px; padding: 0 4px; }
.section-label { font-size: 16px; font-weight: 800; color: var(--ds-ink-1); letter-spacing: 0.3px; }
.section-hint { font-size: 10px; font-weight: 600; color: var(--ds-ink-4); letter-spacing: 1px; }
.list-group { background: var(--ds-surface); border-radius: var(--ds-r-md); overflow: hidden; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.list-item { display: flex; align-items: center; padding: 14px 16px; gap: 14px; transition: background 0.15s; }
.list-item + .list-item { border-top: 1px solid var(--ds-hairline); }
.item-pressed { background: var(--ds-bg-sunken); }
.item-ico { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 12px rgba(10,92,255,0.18); }
.item-body { flex: 1; min-width: 0; }
.item-title { display: block; font-size: 15px; font-weight: 600; color: var(--ds-ink-1); margin-bottom: 2px; }
.item-desc { display: block; font-size: 11px; color: var(--ds-ink-3); }
.item-badge { flex-shrink: 0; }
.badge-num { display: inline-block; min-width: 20px; height: 20px; border-radius: 10px; background: var(--ds-danger); color: #fff; font-size: 11px; font-weight: 700; text-align: center; line-height: 20px; padding: 0 6px; }
.item-chevron { flex-shrink: 0; }
.chevron-char { font-size: 22px; font-weight: 300; color: var(--ds-ink-4); }
.logout-area { padding: 18px 0 0; }
.logout-btn { background: var(--ds-surface); border: 1px solid var(--ds-hairline); border-radius: var(--ds-r-sm); padding: 14px; display: flex; align-items: center; justify-content: center; gap: 8px; transition: background 0.15s; }
.btn-pressed { background: var(--ds-bg-sunken); }
.logout-text { font-size: 16px; font-weight: 600; color: var(--ds-danger); }
</style>
