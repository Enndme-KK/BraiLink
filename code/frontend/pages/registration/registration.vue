<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<text class="nav-title">挂诊</text>
			</view>
		</view>

		<view class="title-area ds-rise ds-d1">
			<text class="page-title">选择医生挂诊</text>
			<text class="page-sub ds-mono">SELECT YOUR DOCTOR</text>
		</view>

		<scroll-view class="content" scroll-y>
			<view class="loading-block" v-if="loading">
				<view class="ds-spinner"></view>
				<text class="loading-text">加载医生列表...</text>
			</view>

			<view v-else class="empty-state" v-if="doctors.length === 0">
				<view class="empty-ico">
					<svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#A2A9BC" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v6a6 6 0 0 0 12 0V3"/><circle cx="20" cy="14" r="2"/></svg>
				</view>
				<text class="empty-text">暂无可挂诊医生</text>
			</view>

			<view v-else class="doctor-list">
				<view class="doctor-card ds-rise" :class="'ds-d' + Math.min(idx + 2, 5)" v-for="(doctor, idx) in doctors" :key="doctor.id || idx">
					<view class="doctor-top">
						<view class="doctor-avatar"><text class="avatar-text">{{ (doctor.name || '医')[0] }}</text></view>
						<view class="doctor-info">
							<view class="doctor-name-row">
								<text class="doctor-name">{{ doctor.name || '医生' }}</text>
								<view class="title-pill"><text>{{ doctor.title || '主治医师' }}</text></view>
							</view>
							<text class="doctor-meta">{{ getSpecialtyText(doctor.specialty) }}</text>
						</view>
					</view>

					<view class="detail-grid">
						<view class="detail-item">
							<text class="detail-label ds-mono">HOSPITAL</text>
							<text class="detail-value">{{ doctor.hospital || '未填写' }}</text>
						</view>
						<view class="detail-item">
							<text class="detail-label ds-mono">DEPT</text>
							<text class="detail-value">{{ doctor.department || '未填写' }}</text>
						</view>
					</view>

					<view class="actions">
						<view class="action-btn ghost" @click="chatWithDoctor(doctor)" hover-class="btn-pressed">
							<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#0A5CFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 20l1-4a8.5 8.5 0 0 1-1-4 8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5z"/></svg>
							<text class="ghost-text">咨询</text>
						</view>
						<view class="action-btn primary" @click="goAppointment(doctor)" hover-class="btn-pressed">
							<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg>
							<text class="primary-text">预约挂号</text>
						</view>
					</view>
				</view>
			</view>

			<view style="height: 90px;"></view>
		</scroll-view>

		<BottomNavPatient current="registration" />
	</view>
</template>

<script>
import BottomNavPatient from '@/components/bottom_nav/BottomNavPatient.vue'
import { doctorAPI } from '@/utils/request.js'

export default {
	name: 'RegistrationPage',
	components: { BottomNavPatient },
	data() { return { loading: false, doctors: [] } },
	async onLoad() {
		const authModule = await import('@/utils/auth.js')
		if (!authModule.requireAuth()) return
		if (authModule.getCurrentUserType() !== 'patient') {
			uni.showToast({ title: '此页面仅限患者访问', icon: 'none' })
			setTimeout(() => uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' }), 1500)
			return
		}
		this.loadDoctors()
	},
	methods: {
		async loadDoctors() {
			this.loading = true
			try {
				const resp = await doctorAPI.getDoctors()
				this.doctors = Array.isArray(resp) ? resp : (resp.results || [])
			} catch (e) { this.doctors = [] }
			finally { this.loading = false }
		},
		getSpecialtyText(s) {
			const map = { neurology: '神经科', radiology: '放射科', oncology: '肿瘤科', neurosurgery: '神经外科', general: '全科' }
			return map[s] || s || '未填写'
		},
		chatWithDoctor(doctor) {
			if (!doctor || !doctor.user) { uni.showToast({ title: '医生信息不完整', icon: 'none' }); return }
			const uid = doctor.user.id || doctor.user_id
			const name = doctor.name || '医生'
			uni.navigateTo({ url: `/pages/chat/chatDialog?patient_id=${uid}&patient_name=${encodeURIComponent(name)}` })
		},
		goAppointment(doctor) {
			uni.navigateTo({ url: `/pages/appointment/appointment?doctorId=${doctor.id}&doctorName=${encodeURIComponent(doctor.name || '')}` })
		}
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); font-family: var(--ds-font); padding-bottom: 80px; }
.navbar { position: sticky; top: 0; z-index: 100; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; padding: 52px 16px 12px; text-align: center; }
.nav-title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); }

.title-area { padding: 18px 20px 16px; }
.page-title { display: block; font-size: 26px; font-weight: 800; color: var(--ds-ink-1); letter-spacing: -0.5px; margin-bottom: 4px; }
.page-sub { display: block; font-size: 11px; font-weight: 600; color: var(--ds-ink-4); letter-spacing: 1px; }

.content { padding: 0 20px; }
.loading-block { display: flex; flex-direction: column; align-items: center; padding: 60px 0; gap: 14px; }
.loading-text { font-size: 13px; color: var(--ds-ink-3); }

.empty-state { display: flex; flex-direction: column; align-items: center; padding: 70px 0; gap: 8px; }
.empty-ico { width: 80px; height: 80px; border-radius: 24px; background: var(--ds-surface); display: flex; align-items: center; justify-content: center; box-shadow: var(--ds-shadow-sm); margin-bottom: 8px; }
.empty-text { font-size: 14px; color: var(--ds-ink-4); }

.doctor-list { display: flex; flex-direction: column; gap: 12px; }
.doctor-card { background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); padding: 16px; }
.doctor-top { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.doctor-avatar { width: 50px; height: 50px; border-radius: 14px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; flex-shrink: 0;  }
.avatar-text { font-size: 20px; font-weight: 800; color: #fff; }
.doctor-info { flex: 1; min-width: 0; }
.doctor-name-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap; }
.doctor-name { font-size: 16px; font-weight: 800; color: var(--ds-ink-1); }
.title-pill { padding: 2px 8px; border-radius: var(--ds-r-pill); background: var(--ds-cyan-soft); }
.title-pill text { font-size: 10px; font-weight: 700; color: #008695; }
.doctor-meta { display: block; font-size: 12px; color: var(--ds-ink-3); }

.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
.detail-item { background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 10px 12px; }
.detail-label { display: block; font-size: 9px; color: var(--ds-ink-4); letter-spacing: 0.8px; margin-bottom: 4px; }
.detail-value { display: block; font-size: 12px; font-weight: 600; color: var(--ds-ink-1); word-break: break-all; }

.actions { display: flex; gap: 10px; }
.action-btn { flex: 1; height: 40px; border-radius: var(--ds-r-sm); display: flex; align-items: center; justify-content: center; gap: 6px; transition: transform 0.18s; }
.action-btn:active, .btn-pressed { transform: scale(0.97); }
.action-btn.ghost { background: var(--ds-brand-soft); }
.ghost-text { font-size: 14px; font-weight: 600; color: var(--ds-brand); }
.action-btn.primary { background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); }
.primary-text { font-size: 14px; font-weight: 600; color: #fff; }
</style>
