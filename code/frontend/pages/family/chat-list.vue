<template>
	<view class="page">
		<view class="hero ds-grid-bg">
			<view class="hero-glow"></view>
			<view class="hero-inner">
				<view class="hero-row ds-rise ds-d1">
					<view class="hero-text">
						<text class="hero-title">医生沟通</text>
						<text class="hero-sub ds-mono">DOCTOR CONTACT</text>
					</view>
					<view class="status-pill" :class="{ active: bound }">
						<view class="status-dot" :class="{ active: bound }"></view>
						<text>{{ bound ? '已绑定' : '待绑定' }}</text>
					</view>
				</view>
			</view>
		</view>

		<scroll-view scroll-y class="content">
			<view class="loading-block" v-if="loading">
				<view class="ds-spinner"></view>
				<text class="loading-text">正在加载医生列表...</text>
			</view>

			<block v-else>
				<!-- 当前患者条 -->
				<view class="patient-strip ds-rise ds-d2" v-if="bound && patient">
					<view class="patient-avatar"><text>{{ getAvatarText(patient.name) }}</text></view>
					<view class="patient-info">
						<text class="patient-label ds-mono">CURRENT PATIENT</text>
						<text class="patient-name">{{ patient.name || '已绑定患者' }}</text>
						<text class="patient-meta">{{ formatPatientMeta(patient) }}</text>
					</view>
					<view class="patient-tag"><text>{{ patient.relationship || '家属' }}</text></view>
				</view>

				<!-- 未绑定 -->
				<view class="empty-card ds-rise ds-d2" v-if="!bound">
					<view class="empty-ico">
						<svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#0A5CFF" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 13a4 4 0 0 0 5.6.5l3-3A4 4 0 0 0 11.9 5l-1.2 1.1"/><path d="M15 11a4 4 0 0 0-5.6-.5l-3 3A4 4 0 0 0 12.1 19l1.2-1.1"/></svg>
					</view>
					<text class="empty-title">先绑定患者，再联系医生</text>
					<text class="empty-desc">绑定成功后，接诊过该患者的医生会自动显示在这里</text>
					<view class="primary-btn" @click="goBindPatient" hover-class="btn-pressed">
						<text class="btn-text">去绑定患者</text>
					</view>
				</view>

				<!-- 暂无医生 -->
				<view class="empty-card ds-rise ds-d2" v-else-if="doctorList.length === 0">
					<view class="empty-ico">
						<svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="#A2A9BC" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v6a6 6 0 0 0 12 0V3"/><circle cx="20" cy="14" r="2"/><path d="M12 15v3a4 4 0 0 0 8 0v-1"/></svg>
					</view>
					<text class="empty-title">暂无可沟通医生</text>
					<text class="empty-desc">待医生接诊或产生相关就诊记录后会自动出现</text>
					<view class="secondary-btn" @click="loadRelatedDoctors" hover-class="btn-pressed">
						<text class="btn-secondary-text">刷新列表</text>
					</view>
				</view>

				<!-- 医生列表 -->
				<view v-else>
					<view class="section-head">
						<view>
							<text class="section-label">可沟通医生</text>
							<text class="section-hint ds-mono">{{ doctorList.length }} DOCTORS</text>
						</view>
						<view class="refresh-pill" @click="loadRelatedDoctors"><text>刷新</text></view>
					</view>

					<view class="doctor-card ds-rise" :class="'ds-d' + Math.min(i + 3, 5)" v-for="(doctor, i) in doctorList" :key="`${doctor.doctor_id || doctor.doctor_user_id || doctor.id}-${doctor.patient_id || 'patient'}`" @click="openChat(doctor)" hover-class="card-pressed">
						<view class="doctor-top">
							<view class="doctor-avatar"><text>{{ getAvatarText(getDoctorName(doctor)) }}</text></view>
							<view class="doctor-main">
								<view class="doctor-name-row">
									<text class="doctor-name">{{ getDoctorName(doctor) }}</text>
									<view class="doctor-title-tag" v-if="doctor.title"><text>{{ doctor.title }}</text></view>
								</view>
								<text class="doctor-meta">{{ formatDoctorMeta(doctor) }}</text>
								<text class="doctor-specialty" v-if="doctor.specialty">擅长 · {{ doctor.specialty }}</text>
							</view>
						</view>

						<view class="doctor-grid">
							<view class="info-item">
								<text class="info-label ds-mono">DEPT</text>
								<text class="info-value">{{ doctor.department || '未填写' }}</text>
							</view>
							<view class="info-item">
								<text class="info-label ds-mono">PATIENT</text>
								<text class="info-value">{{ doctor.patient_name || patientNameFallback }}</text>
							</view>
							<view class="info-item">
								<text class="info-label ds-mono">RELATION</text>
								<text class="info-value">{{ doctor.relationship || patientRelationshipFallback }}</text>
							</view>
							<view class="info-item">
								<text class="info-label ds-mono">VISIT</text>
								<text class="info-value">{{ formatDateTime(doctor.latest_visit_date) }}</text>
							</view>
						</view>

						<view class="doctor-footer">
							<text class="footer-tip">进入沟通</text>
							<text class="footer-arrow">›</text>
						</view>
					</view>
				</view>
			</block>
			<view style="height: 24px;"></view>
		</scroll-view>

		<bottom-nav-family current="chat" />
	</view>
</template>

<script>
import { familyAPI } from '@/utils/request.js'
import { requireAuth, getCurrentUserType } from '@/utils/auth.js'
import BottomNavFamily from '@/components/bottom_nav/BottomNavFamily.vue'

export default {
	name: 'FamilyChatList',
	components: { BottomNavFamily },
	data() {
		return { loading: false, doctorList: [], bound: false, patient: null }
	},
	computed: {
		patientNameFallback() { return this.patient && this.patient.name ? this.patient.name : '已绑定患者' },
		patientRelationshipFallback() { return this.patient && this.patient.relationship ? this.patient.relationship : '家属' }
	},
	onLoad() {
		if (!requireAuth()) return
		if (!this.ensureFamilyUser()) return
		this.loadRelatedDoctors()
	},
	onShow() {
		if (!requireAuth()) return
		if (!this.ensureFamilyUser()) return
		this.loadRelatedDoctors()
	},
	methods: {
		ensureFamilyUser() {
			if (getCurrentUserType() !== 'family') {
				uni.showToast({ title: '仅家属可访问', icon: 'none' })
				uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' })
				return false
			}
			return true
		},
		async loadRelatedDoctors() {
			this.loading = true
			try {
				const summary = await familyAPI.getHomeSummary()
				this.bound = !!summary.bound
				this.patient = summary.patient || null
				if (!this.bound) { this.doctorList = []; return }
				const doctors = await familyAPI.getRelatedDoctors()
				this.doctorList = Array.isArray(doctors) ? doctors : []
			} catch (e) {
				this.bound = false; this.patient = null; this.doctorList = []
				uni.showToast({ title: e?.response?.data?.error || e?.message || '加载失败', icon: 'none' })
			} finally { this.loading = false }
		},
		openChat(doctor) {
			const partnerUserId = doctor.doctor_user_id || doctor.user_id || doctor.doctor_id || doctor.id || ''
			const partnerName = encodeURIComponent(this.getDoctorName(doctor))
			const patientName = encodeURIComponent(doctor.patient_name || this.patientNameFallback || '')
			const relationship = encodeURIComponent(doctor.relationship || this.patientRelationshipFallback || '')
			uni.navigateTo({ url: `/pages/chat/chatDialog?partner_user_id=${partnerUserId}&partner_name=${partnerName}&partner_role=doctor&patient_name=${patientName}&relationship=${relationship}` })
		},
		goBindPatient() { uni.navigateTo({ url: '/pages/family/bind' }) },
		getDoctorName(d) { return d.doctor_name || d.name || '未命名医生' },
		getAvatarText(name) { return name ? String(name).slice(0, 1) : '医' },
		formatPatientMeta(p) {
			let g = p.gender || '性别待完善'
			if (g === 'male' || g === 'M' || g === '男') g = '男'
			if (g === 'female' || g === 'F' || g === '女') g = '女'
			const age = p.age ? `${p.age}岁` : '年龄待完善'
			return `${g} · ${age}`
		},
		formatDoctorMeta(d) {
			const parts = [d.hospital, d.department].filter(Boolean)
			return parts.length ? parts.join(' · ') : '已接诊医生'
		},
		formatDateTime(v) {
			if (!v) return '暂无'
			const d = new Date(v); if (isNaN(d.getTime())) return v
			return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
		}
	}
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: var(--ds-bg); font-family: var(--ds-font); }

.hero { position: relative; padding: 78px 24px 28px; background: linear-gradient(160deg, #0C1733 0%, #0A3A8C 55%, #0A5CFF 130%); overflow: hidden; flex-shrink: 0; }
.hero-glow { position: absolute; top: -60px; right: -60px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(0,194,215,0.45) 0%, transparent 70%); filter: blur(8px); }
.hero-inner { position: relative; }
.hero-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.hero-text { flex: 1; min-width: 0; }
.hero-title { display: block; font-size: 24px; font-weight: 800; color: #fff; letter-spacing: 0.5px; margin-bottom: 4px; }
.hero-sub { display: block; font-size: 10px; font-weight: 600; color: rgba(255,255,255,0.7); letter-spacing: 1.5px; }
.status-pill { display: flex; align-items: center; gap: 6px; padding: 6px 12px; background: rgba(255,255,255,0.13); border: 1px solid rgba(255,255,255,0.18); border-radius: var(--ds-r-pill); flex-shrink: 0; }
.status-pill text { font-size: 12px; font-weight: 600; color: #fff; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--ds-warning); }
.status-pill.active .status-dot { background: var(--ds-success); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(31,184,119,0.5); } 70% { box-shadow: 0 0 0 6px rgba(31,184,119,0); } 100% { box-shadow: 0 0 0 0 rgba(31,184,119,0); } }

.content { flex: 1; padding: 16px 20px 90px; box-sizing: border-box; }

.loading-block { display: flex; flex-direction: column; align-items: center; padding: 70px 20px; gap: 14px; }
.loading-text { font-size: 13px; color: var(--ds-ink-3); }

.patient-strip { display: flex; align-items: center; gap: 12px; padding: 14px; background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); margin-bottom: 14px; }
.patient-avatar { width: 46px; height: 46px; border-radius: 14px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; flex-shrink: 0;  }
.patient-avatar text { color: #fff; font-size: 18px; font-weight: 800; }
.patient-info { flex: 1; min-width: 0; }
.patient-label { display: block; font-size: 10px; color: var(--ds-ink-4); letter-spacing: 0.8px; margin-bottom: 4px; }
.patient-name { display: block; font-size: 16px; font-weight: 800; color: var(--ds-ink-1); margin-bottom: 3px; }
.patient-meta { display: block; font-size: 11px; color: var(--ds-ink-3); }
.patient-tag { padding: 4px 10px; border-radius: var(--ds-r-pill); background: var(--ds-cyan-soft); flex-shrink: 0; }
.patient-tag text { font-size: 11px; font-weight: 700; color: #008695; }

.empty-card { background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); padding: 32px 22px; text-align: center; }
.empty-ico { width: 76px; height: 76px; border-radius: 22px; background: var(--ds-brand-soft); display: flex; align-items: center; justify-content: center; margin: 0 auto 14px; }
.empty-title { display: block; font-size: 18px; font-weight: 800; color: var(--ds-ink-1); margin-bottom: 8px; }
.empty-desc { display: block; font-size: 13px; line-height: 1.65; color: var(--ds-ink-3); margin-bottom: 20px; }

.primary-btn { height: 46px; border-radius: var(--ds-r-sm); background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); display: flex; align-items: center; justify-content: center; transition: transform 0.18s; }
.primary-btn:active, .btn-pressed { transform: scale(0.97); }
.btn-text { font-size: 15px; font-weight: 600; color: #fff; }
.secondary-btn { height: 46px; border-radius: var(--ds-r-sm); background: var(--ds-brand-soft); display: flex; align-items: center; justify-content: center; }
.btn-secondary-text { font-size: 15px; font-weight: 600; color: var(--ds-brand); }

.section-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 12px; padding: 0 4px; }
.section-label { display: block; font-size: 16px; font-weight: 800; color: var(--ds-ink-1); }
.section-hint { display: block; margin-top: 4px; font-size: 10px; font-weight: 600; color: var(--ds-ink-4); letter-spacing: 1px; }
.refresh-pill { padding: 6px 12px; border-radius: var(--ds-r-pill); background: var(--ds-brand-soft); flex-shrink: 0; }
.refresh-pill text { font-size: 12px; font-weight: 600; color: var(--ds-brand); }

.doctor-card { background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); padding: 16px; margin-bottom: 12px; transition: transform 0.18s var(--ds-ease); }
.card-pressed { transform: scale(0.99); box-shadow: var(--ds-shadow-md); }
.doctor-top { display: flex; align-items: flex-start; gap: 12px; }
.doctor-avatar { width: 48px; height: 48px; border-radius: 14px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; flex-shrink: 0;  }
.doctor-avatar text { color: #fff; font-size: 18px; font-weight: 800; }
.doctor-main { flex: 1; min-width: 0; }
.doctor-name-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap; }
.doctor-name { font-size: 16px; font-weight: 800; color: var(--ds-ink-1); }
.doctor-title-tag { padding: 2px 8px; border-radius: var(--ds-r-pill); background: var(--ds-cyan-soft); }
.doctor-title-tag text { font-size: 10px; font-weight: 700; color: #008695; }
.doctor-meta { display: block; font-size: 12px; color: var(--ds-ink-3); line-height: 1.55; }
.doctor-specialty { display: block; font-size: 12px; color: var(--ds-ink-3); margin-top: 3px; }

.doctor-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 14px; }
.info-item { background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 10px 12px; }
.info-label { display: block; font-size: 9px; color: var(--ds-ink-4); letter-spacing: 0.8px; margin-bottom: 4px; }
.info-value { display: block; font-size: 12px; font-weight: 600; color: var(--ds-ink-1); word-break: break-all; }

.doctor-footer { display: flex; align-items: center; justify-content: flex-end; gap: 4px; margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--ds-hairline); }
.footer-tip { font-size: 12px; font-weight: 600; color: var(--ds-brand); }
.footer-arrow { font-size: 18px; line-height: 1; color: var(--ds-brand); }
</style>
