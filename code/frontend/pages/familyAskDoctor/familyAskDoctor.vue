<template>
	<view class="family-ask-page">
		<!-- 顶部导航 -->
		<view class="header">
			<view class="header-left" @click="goBack">
				<text class="back-icon">←</text>
			</view>
			<view class="header-center">
				<text class="title">询问医生</text>
				<text class="subtitle">选择医生发起对话</text>
			</view>
			<view class="header-right"></view>
		</view>

		<!-- 医生列表 -->
		<scroll-view class="list" scroll-y>
			<view class="empty" v-if="loading">
				<view class="spinner"></view>
				<text class="empty-text">加载中...</text>
			</view>
			<view class="empty" v-else-if="doctors.length === 0">
				<text class="empty-icon">🩺</text>
				<text class="empty-text">暂无医生</text>
			</view>
			<view class="card" v-for="(d, idx) in doctors" :key="d.id || idx" @click="startChat(d)">
				<view class="avatar">{{ (d.name || d.user?.username || '医')[0] }}</view>
				<view class="info">
					<view class="name-row">
						<text class="name">{{ d.name || d.user?.name || d.user?.username || '医生' }}</text>
						<text class="dept">{{ specialtyName(d.specialty) || d.department || '—' }}</text>
					</view>
					<text class="hospital">{{ d.hospital || '—' }}</text>
				</view>
				<view class="arrow">→</view>
			</view>
		</scroll-view>

		<!-- 底部导航 家属端 -->
		<bottom-nav-family current="ask"></bottom-nav-family>
	</view>
</template>

<script>
import BottomNavFamily from '@/components/bottom_nav/BottomNavFamily.vue'
import { doctorAPI } from '@/utils/request.js'

export default {
	components: { BottomNavFamily },
	data() {
		return {
			loading: false,
			doctors: []
		}
	},
	async onLoad() {
		// 需要已登录
		const { requireAuth } = await import('@/utils/auth.js')
		if (!requireAuth()) return
		this.loadDoctors()
	},
	methods: {
		async loadDoctors() {
			try {
				this.loading = true
				const res = await doctorAPI.getDoctors()
				this.doctors = Array.isArray(res) ? res : (res.results || [])
			} catch (e) {
				console.error('加载医生失败', e)
				uni.showToast({ title: '加载失败', icon: 'none' })
			} finally {
				this.loading = false
			}
		},
		specialtyName(code) {
			const map = { neurology: '神经科', radiology: '放射科', oncology: '肿瘤科', neurosurgery: '神经外科', general: '全科' }
			return map[code] || code
		},
		startChat(doctor) {
			// chatDialog 接口期望 patient_id 为对方用户ID（其实现为 partnerId）
			const recipientId = String(doctor.user?.id || doctor.user_id || doctor.id)
			const name = encodeURIComponent(doctor.name || doctor.user?.name || '医生')
			uni.navigateTo({
				url: `/pages/chat/chatDialog?patient_id=${recipientId}&patient_name=${name}`
			})
		},
		goBack() { uni.navigateBack() }
	}
}
</script>

<style scoped>
.family-ask-page { min-height: 100vh; background: var(--ds-bg); padding-bottom: 80px; font-family: var(--ds-font); }
.header { background: rgba(244,246,251,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); padding: 52px 16px 12px; display: flex; align-items: center; border-bottom: 1px solid var(--ds-hairline); }
.header-left, .header-right { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
.header-left:active { background: var(--ds-brand-ghost); }
.back-icon { font-size: 28px; color: var(--ds-brand); font-weight: 300; line-height: 1; margin-top: -3px; }
.header-center { flex: 1; text-align: center; }
.title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); }
.subtitle { display: block; font-size: 11px; color: var(--ds-ink-4); margin-top: 2px; font-family: var(--ds-font-mono); letter-spacing: 0.5px; }
.list { height: calc(100vh - 140px); padding: 14px 20px 0; }
.card { display: flex; align-items: center; gap: 12px; background: var(--ds-surface); border: 1px solid var(--ds-hairline); border-radius: var(--ds-r-md); padding: 14px; margin-bottom: 10px; box-shadow: var(--ds-shadow-sm); transition: transform 0.18s; }
.card:active { transform: scale(0.99); }
.avatar { width: 44px; height: 44px; border-radius: 14px; background: var(--ds-grad-brand); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px; flex-shrink: 0; box-shadow: 0 4px 10px rgba(10,92,255,0.2); }
.info { flex: 1; min-width: 0; }
.name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px; }
.name { font-size: 15px; font-weight: 700; color: var(--ds-ink-1); }
.dept { padding: 2px 8px; border-radius: var(--ds-r-pill); background: var(--ds-cyan-soft); font-size: 10px; font-weight: 700; color: #008695; }
.hospital { font-size: 12px; color: var(--ds-ink-3); }
.arrow { color: var(--ds-ink-4); font-size: 20px; }
.empty { padding: 80px 20px; text-align: center; }
.empty-icon { font-size: 48px; opacity: 0.3; display: block; margin-bottom: 8px; }
.empty-text { font-size: 14px; color: var(--ds-ink-4); }
.spinner { width: 32px; height: 32px; border: 2px solid var(--ds-hairline); border-top-color: var(--ds-brand); border-radius: 50%; margin: 0 auto 10px; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>

