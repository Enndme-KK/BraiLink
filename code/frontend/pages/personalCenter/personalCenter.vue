<template>
	<view class="page">
		<view class="hero ds-scanline ds-grid-bg">
			<view class="hero-glow"></view>
			<view class="hero-inner">
				<view class="user-row ds-rise ds-d1">
					<view class="avatar-box">
						<image :src="doctor.img_url" class="avatar-img" mode="aspectFill" />
						<view class="avatar-tag"><text class="avatar-tag-text">医生</text></view>
					</view>
					<view class="user-info">
						<view class="name-row">
							<text class="user-name" v-if="name_display">{{ doctor.name }}</text>
							<text class="user-name" v-else>*{{ doctor.name.substring(1) }}</text>
							<view class="eye-btn" @click="change_eye_status">
								<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="rgba(255,255,255,0.85)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
									<path v-if="name_display" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/>
									<circle v-if="name_display" cx="12" cy="12" r="3"/>
									<path v-else d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-7-11-7a18.45 18.45 0 0 1 5.06-5.94"/>
									<path v-else d="M1 1l22 22"/>
								</svg>
							</view>
						</view>
						<view class="id-row" v-if="doctor.card_id">
							<text class="user-id ds-mono" v-if="id_card_display">执业证号 · {{ doctor.card_id }}</text>
							<text class="user-id ds-mono" v-else>执业证号 · ****{{ doctor.card_id.length > 4 ? doctor.card_id.substring(doctor.card_id.length - 4) : '' }}</text>
							<view class="eye-btn" @click="change_eye_status2">
								<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
									<path v-if="id_card_display" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/>
									<circle v-if="id_card_display" cx="12" cy="12" r="3"/>
									<path v-else d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-7-11-7a18.45 18.45 0 0 1 5.06-5.94"/>
									<path v-else d="M1 1l22 22"/>
								</svg>
							</view>
						</view>
						<view class="id-row" v-else><text class="user-id ds-mono">执业证号 · 未设置</text></view>
						<view class="user-tags">
							<view class="tag-pill"><text class="tag-text">{{ doctor.gender }}</text></view>
							<view class="tag-pill"><text class="tag-text">{{ doctor.department }}</text></view>
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
				<view class="list-item" v-for="(setting, index) in setting_list" :key="index" @click="toPage(index)" hover-class="item-pressed">
					<view class="item-ico" :style="{ background: getIconBg(index) }">
						<view v-html="getSettingSvg(index)"></view>
					</view>
					<view class="item-body">
						<text class="item-title">{{ setting }}</text>
						<text class="item-desc">{{ getSettingDesc(index) }}</text>
					</view>
					<view class="item-badge" v-if="index === 3 && unreadNotificationCount > 0">
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

		<bottom-nav-doctor current="profile"></bottom-nav-doctor>
	</view>
</template>

<script>
import BottomNavDoctor from '@/components/bottom_nav/BottomNavDoctor.vue'
import { doctorAPI, notificationAPI } from '@/utils/request.js'

const SETTING_SVG = {
	profile: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16l-3-2-2 2-2-2-2 2-2-2-3 2z"/><path d="M9 7h6M9 11h6M9 15h4"/></svg>',
	account: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M5 21v-1a7 7 0 0 1 14 0v1"/></svg>',
	pwd: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
	notice: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 16v-5a6 6 0 0 0-12 0v5l-2 2v1h16v-1l-2-2z"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>',
	feedback: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 20l1-4a8.5 8.5 0 0 1-1-4 8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5z"/></svg>',
	about: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'
}

export default {
	components: { BottomNavDoctor },
	data() {
		return {
			doctor: { name: '加载中...', gender: '未知', card_id: '', department: '', img_url: '../../static/resource/img2.jpg' },
			setting_list: ['完善档案', '账号管理', '修改密码', '意见反馈', '关于我们'],
			name_display: false, id_card_display: false, loading: true, unreadNotificationCount: 0
		}
	},
	onLoad() { this.loadDoctorInfo(); this.loadUnreadNotificationCount() },
	onShow() { this.loadUnreadNotificationCount() },
	methods: {
		async loadDoctorInfo() {
			this.loading = true
			try {
				const r = await doctorAPI.getMyProfile()
				if (r) {
					const u = r.user || {}
					this.doctor = {
						name: r.name || u.name || '未知',
						gender: u.gender || '未知',
						card_id: r.license_number || '',
						department: r.department || (r.specialty ? this.getSpecialtyName(r.specialty) : '未设置'),
						img_url: u.avatar || '../../static/resource/img2.jpg'
					}
				}
			} catch (e) {
				if (e.message?.includes('未找到') || e.message?.includes('404')) {
					try {
						const r = await (await import('@/utils/request.js')).authAPI.getProfile()
						if (r) this.doctor = { name: r.name || r.username || '未设置', gender: '未知', card_id: '', department: '请完善档案', img_url: r.avatar || '../../static/resource/img2.jpg' }
					} catch (e2) {}
					uni.showModal({
						title: '提示', content: '您尚未完善医生档案，是否现在去完善？',
						confirmText: '去完善', cancelText: '稍后',
						success: r => { if (r.confirm) uni.navigateTo({ url: '/pages/completeProfile/completeProfile?userType=doctor&isNew=true' }) }
					})
				} else uni.showToast({ title: '加载失败', icon: 'none' })
			} finally { this.loading = false }
		},
		getSpecialtyName(s) { return { neurology: '神经科', radiology: '放射科', oncology: '肿瘤科', neurosurgery: '神经外科', general: '全科' }[s] || s },
		change_eye_status() { this.name_display = !this.name_display },
		change_eye_status2() { this.id_card_display = !this.id_card_display },
		toPage(i) {
			const p = [
				'/pages/completeProfile/completeProfile?userType=doctor',
				'/pages/settings/account/account',
				'/pages/settings/updatePwd/updatePwd',
				'/pages/settings/feedback/feedback',
				'/pages/settings/about/about'
			]
			if (p[i]) uni.navigateTo({ url: p[i] })
		},
		getSettingSvg(i) { return [SETTING_SVG.profile, SETTING_SVG.account, SETTING_SVG.pwd, SETTING_SVG.feedback, SETTING_SVG.about][i] || SETTING_SVG.about },
		getSettingDesc(i) { return ['完善医生档案信息', '管理个人信息', '修改登录密码', '提交您的建议', '软件版本信息'][i] || '' },
		getIconBg(i) {
			const list = [
				'linear-gradient(135deg, #0A5CFF 0%, #00C2D7 100%)',
				'linear-gradient(135deg, #0A5CFF 0%, #0742C4 100%)',
				'linear-gradient(135deg, #1FB877 0%, #00C2D7 100%)',
				'linear-gradient(135deg, #F5A623 0%, #FF7A59 100%)',
				'linear-gradient(135deg, #00C2D7 0%, #0A5CFF 100%)',
				'linear-gradient(135deg, #69728C 0%, #2B3658 100%)'
			]
			return list[i] || list[5]
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
.name-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.user-name { font-size: 22px; font-weight: 800; color: #fff; }
.eye-btn { width: 24px; height: 24px; border-radius: 8px; background: rgba(255,255,255,0.13); border: 1px solid rgba(255,255,255,0.18); display: flex; align-items: center; justify-content: center; }
.id-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.user-id { font-size: 12px; color: rgba(255,255,255,0.78); letter-spacing: 0.3px; }
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
