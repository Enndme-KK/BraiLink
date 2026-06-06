<template>
	<view class="page">
		<!-- Hero -->
		<view class="hero">
			<view class="hero-inner">
				<view class="hero-row ds-rise ds-d1">
					<view class="hero-greet">
						<text class="hero-hello">{{ greetingText }}</text>
						<text class="hero-name">{{ familyName }}</text>
					</view>
					<view class="status-pill" :class="{ active: bound }">
						<view class="status-dot"></view>
						<text>{{ bound ? '已绑定' : '待绑定' }}</text>
					</view>
				</view>
				<view class="hero-sub-row ds-rise ds-d2">
					<view class="sub-line"></view>
					<text class="hero-sub">家属关怀 · 健康同行</text>
					<view class="sub-line"></view>
				</view>
			</view>
		</view>

		<view class="content-wrap">
			<view class="content">
			<!-- 加载 -->
			<view class="loading-block" v-if="loading">
				<view class="ds-spinner"></view>
				<text class="loading-text">正在加载家属端信息...</text>
			</view>

			<block v-else>
				<!-- 未绑定 -->
				<view class="unbound-card ds-rise ds-d2" v-if="!bound">
					<view class="unbound-body">
						<view class="unbound-ico">
							<svg viewBox="0 0 24 24" width="44" height="44" fill="none" stroke="#0A5CFF" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 13a4 4 0 0 0 5.6.5l3-3A4 4 0 0 0 11.9 5l-1.2 1.1"/><path d="M15 11a4 4 0 0 0-5.6-.5l-3 3A4 4 0 0 0 12.1 19l1.2-1.1"/></svg>
						</view>
						<text class="unbound-title">绑定患者后开始使用</text>
						<text class="unbound-desc">请输入患者端生成的邀请码，绑定后即可查看病历摘要、挂号信息并联系医生。</text>
					</view>
					<view class="primary-btn" @click="goBindPage" hover-class="btn-pressed">
						<text class="btn-text">去绑定患者</text>
					</view>
				</view>

				<block v-else>
					<!-- 患者卡 -->
					<view class="patient-card ds-rise ds-d2">
						<view class="patient-top">
							<view class="patient-avatar">
								<text class="avatar-text">{{ getAvatarText(patient && patient.name) }}</text>
							</view>
							<view class="patient-main">
								<text class="patient-name">{{ patient.name }}</text>
								<text class="patient-meta">{{ formatGender(patient.gender) }} · {{ patient.age || '年龄待完善' }}岁</text>
							</view>
							<view class="relation-tag">
								<text>{{ patient.relationship || '家属' }}</text>
							</view>
						</view>
						<view class="patient-grid">
							<view class="patient-info-item">
								<text class="info-label">联系电话</text>
								<text class="info-value">{{ patient.phone || '未填写' }}</text>
							</view>
							<view class="patient-info-item">
								<text class="info-label">绑定时间</text>
								<text class="info-value">{{ formatDateTime(patient.binding_time) }}</text>
							</view>
						</view>
					</view>

					<!-- 快捷入口 -->
					<view class="quick-grid ds-rise ds-d3">
						<view class="quick-card" @click="goChatPage" hover-class="item-pressed">
							<view class="quick-icon-box brand">
								<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 20l1-4a8.5 8.5 0 0 1-1-4 8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5z"/></svg>
							</view>
							<text class="quick-title">联系医生</text>
							<text class="quick-desc">查看可沟通医生</text>
						</view>
						<view class="quick-card" @click="goAiPage" hover-class="item-pressed">
							<view class="quick-icon-box cyan">
								<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 8V4.5"/><circle cx="9" cy="13.5" r="1.1" fill="#fff" stroke="none"/><circle cx="15" cy="13.5" r="1.1" fill="#fff" stroke="none"/><path d="M2 12.5v3M22 12.5v3"/></svg>
							</view>
							<text class="quick-title">AI 助手</text>
							<text class="quick-desc">护理问题咨询</text>
						</view>
						<view class="quick-card" @click="goBindPage" hover-class="item-pressed">
							<view class="quick-icon-box success">
								<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 13a4 4 0 0 0 5.6.5l3-3A4 4 0 0 0 11.9 5l-1.2 1.1"/><path d="M15 11a4 4 0 0 0-5.6-.5l-3 3A4 4 0 0 0 12.1 19l1.2-1.1"/></svg>
							</view>
							<text class="quick-title">绑定管理</text>
							<text class="quick-desc">添加或解除绑定</text>
						</view>
						<view class="quick-card" @click="goProfilePage" hover-class="item-pressed">
							<view class="quick-icon-box warning">
								<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M5 21v-1a7 7 0 0 1 14 0v1"/></svg>
							</view>
							<text class="quick-title">我的</text>
							<text class="quick-desc">账号与退出</text>
						</view>
					</view>

					<!-- 病历记录 -->
					<view class="section ds-rise ds-d4">
						<view class="section-header">
							<view>
								<text class="section-title">病历记录</text>
								<text class="section-sub">最近就诊与诊断摘要</text>
							</view>
							<text class="section-count">{{ medicalRecords.length }} 条</text>
						</view>
						<view class="empty-block" v-if="medicalRecords.length === 0">
							<view class="empty-ico">
								<svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#A2A9BC" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></svg>
							</view>
							<text class="empty-title">暂无病例记录</text>
							<text class="empty-desc">医生接诊并完善病例后会显示在这里</text>
						</view>
						<view class="record-card" v-for="record in medicalRecords" :key="record.id" @click="goRecordDetail(record)" hover-class="item-pressed">
							<view class="record-top">
								<text class="record-title">{{ record.check_project || record.department || '检查记录' }}</text>
								<view class="record-status" :class="`status-${record.status || 'pending'}`">
									<text>{{ getStatusText(record.status) }}</text>
								</view>
							</view>
							<text class="record-time ds-mono">{{ formatDateTime(record.visit_date) }}</text>
							<view class="record-info">
								<text v-if="record.patient_name">患者：{{ record.patient_name }}{{ formatRelationship(record.relationship) }}</text>
								<text>科室：{{ record.department || '未填写' }}</text>
								<text>医生：{{ record.doctor_name || '未分配' }}</text>
							</view>
							<text class="record-diagnosis">{{ record.diagnosis || record.notes || '暂无诊断摘要' }}</text>
							<view class="record-action">
								<text class="record-action-text">查看详细报告</text>
								<text class="record-action-arrow">›</text>
							</view>
						</view>
					</view>

					<!-- 挂号 -->
					<view class="section ds-rise ds-d5">
						<view class="section-header">
							<view>
								<text class="section-title">挂号信息</text>
								<text class="section-sub">挂号与就诊状态</text>
							</view>
							<text class="section-count">{{ registrations.length }} 条</text>
						</view>
						<view class="empty-block" v-if="registrations.length === 0">
							<view class="empty-ico">
								<svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#A2A9BC" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg>
							</view>
							<text class="empty-title">暂无挂号信息</text>
							<text class="empty-desc">患者提交挂号后会同步展示医生接诊状态</text>
						</view>
						<view class="record-card compact" v-for="item in registrations" :key="`reg-${item.id}`" @click="toAppointmentDetail(item)">
							<view class="record-top">
								<text class="record-title">{{ item.appointment_type_display || item.check_project || '预约挂号' }}</text>
								<view class="record-status" :class="`status-${item.status}`">
									<text>{{ getAppointmentStatusText(item.status, item.status_display) }}</text>
								</view>
							</view>
							<text class="record-time ds-mono">{{ formatDateTime(item.visit_date) }}</text>
							<view class="record-info">
								<text v-if="item.patient_name">患者：{{ item.patient_name }}{{ formatRelationship(item.relationship) }}</text>
								<text>科室：{{ item.department || '未填写' }}</text>
								<text>医生：{{ item.doctor_name || '未分配' }}</text>
								<text v-if="item.symptoms">主诉：{{ item.symptoms }}</text>
								<text v-if="item.reject_reason" class="reject-reason">拒绝原因：{{ item.reject_reason }}</text>
							</view>
						</view>
					</view>
				</block>
			</block>
		</view>
		</view>

		<bottom-nav-family current="home" />
	</view>
</template>

<script>
import { familyAPI } from '@/utils/request.js'
import { requireAuth, getCurrentUserType, getCurrentUser } from '@/utils/auth.js'
import BottomNavFamily from '@/components/bottom_nav/BottomNavFamily.vue'

export default {
	name: 'FamilyIndex',
	components: { BottomNavFamily },
	data() {
		return {
			loading: true,
			bound: false,
			patient: null,
			medicalRecords: [],
			registrations: [],
			familyName: '家属'
		}
	},
	computed: {
		greetingText() {
			const h = new Date().getHours()
			if (h < 6) return '夜深了，'
			if (h < 12) return '早上好，'
			if (h < 14) return '中午好，'
			if (h < 18) return '下午好，'
			return '晚上好，'
		}
	},
	onLoad() {
		if (!requireAuth()) return
		if (!this.ensureFamilyUser()) return
		const u = getCurrentUser(); this.familyName = (u && (u.name || u.username)) || '家属'
		this.loadHomeSummary()
	},
	onShow() {
		if (!requireAuth()) return
		if (!this.ensureFamilyUser()) return
		this.loadHomeSummary()
	},
	methods: {
		ensureFamilyUser() {
			const userType = getCurrentUserType()
			if (userType !== 'family') {
				uni.showToast({ title: '仅家属可访问', icon: 'none' })
				uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' })
				return false
			}
			return true
		},
		async loadHomeSummary() {
			this.loading = true
			try {
				const data = await familyAPI.getHomeSummary()
				this.bound = !!data.bound
				this.patient = data.patient || null
				this.medicalRecords = Array.isArray(data.medical_records) ? data.medical_records : []
				this.registrations = Array.isArray(data.registrations) ? data.registrations : []
			} catch (error) {
				console.error('加载家属首页失败:', error)
				const message = error?.response?.data?.error || error?.message || '加载失败'
				uni.showToast({ title: message, icon: 'none' })
			} finally {
				this.loading = false
			}
		},
		goBindPage() { uni.navigateTo({ url: '/pages/family/bind' }) },
		goChatPage() { uni.reLaunch({ url: '/pages/family/chat-list' }) },
		goAiPage() { uni.reLaunch({ url: '/pages/family/ai-assistant' }) },
		goProfilePage() { uni.reLaunch({ url: '/pages/family/profile' }) },
		goRecordDetail(record) {
			if (!record || !record.id) { uni.showToast({ title: '缺少病历信息', icon: 'none' }); return }
			uni.navigateTo({ url: `/pages/previewReport/previewReport?recordId=${record.id}` })
		},
		toAppointmentDetail(item) {
			if (!item || !item.id) return
			uni.showModal({
				title: item.appointment_type_display || '挂号详情',
				content: `状态：${this.getAppointmentStatusText(item.status, item.status_display)}\n科室：${item.department || '未填写'}\n医生：${item.doctor_name || '未分配'}\n日期：${this.formatDateTime(item.visit_date)}${item.symptoms ? '\n主诉：' + item.symptoms : ''}${item.reject_reason ? '\n拒绝原因：' + item.reject_reason : ''}`,
				showCancel: false
			})
		},
		getAvatarText(name) { return name ? String(name).slice(0, 1) : '患' },
		formatGender(value) {
			if (value === '男' || value === 'M') return '男'
			if (value === '女' || value === 'F') return '女'
			return value || '性别待完善'
		},
		formatRelationship(value) { return value ? `（${value}）` : '' },
		getStatusText(status) {
			const map = { pending: '待处理', processing: '处理中', completed: '已完成', cancelled: '已取消' }
			return map[status] || status || '待处理'
		},
		getAppointmentStatusText(status, statusDisplay) {
			const map = { pending: '待接诊', accepted: '已接诊', rejected: '已拒绝', cancelled: '已取消', completed: '已完成' }
			return statusDisplay || map[status] || status || '待接诊'
		},
		formatDateTime(value) {
			if (!value) return '—'
			const d = new Date(value); if (isNaN(d.getTime())) return value
			const y = d.getFullYear(), m = String(d.getMonth()+1).padStart(2,'0'), dd = String(d.getDate()).padStart(2,'0')
			const hh = String(d.getHours()).padStart(2,'0'), mm = String(d.getMinutes()).padStart(2,'0')
			return `${y}-${m}-${dd} ${hh}:${mm}`
		}
	}
}
</script>

<style scoped>
.page {
	min-height: 100vh;
	display: flex;
	flex-direction: column;
	font-family: var(--ds-font);
	padding-bottom: calc(70px + env(safe-area-inset-bottom));
	/* 整页一条渐变：上 30% 深空蓝，下 70% 平滑过渡到冷灰白 */
	background: linear-gradient(180deg,
		#0C1733 0%,
		#0A3A8C 10%,
		#0A5CFF 22%,
		#5A8DFF 30%,
		#A8C0EE 45%,
		#CCD7EC 60%,
		#DDE4F0 80%,
		#E6EBF3 100%);
}

/* Hero — 自身透明，让页面渐变透过；不再有半圆光晕、扫描线、点阵 */
.hero {
	position: relative;
	padding: 78px 24px 56px;
	background: transparent;
	overflow: hidden;
}
.hero-inner { position: relative; }
.hero-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.hero-greet { display: flex; flex-direction: column; gap: 4px; min-width: 0; flex: 1; }
.hero-hello { font-size: 20px; color: rgba(255,255,255,0.82); font-weight: 500; letter-spacing: 0.3px; }
.hero-name { font-size: 44px; font-weight: 800; color: #fff; letter-spacing: 0.5px; line-height: 1.1; word-break: break-all; }
.status-pill { display: flex; align-items: center; gap: 6px; padding: 6px 12px; background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.25); border-radius: var(--ds-r-pill); flex-shrink: 0; margin-top: 8px; }
.status-pill text { font-size: 12px; font-weight: 600; color: #fff; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--ds-warning); }
.status-pill.active .status-dot { background: var(--ds-success); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(31,184,119,0.5); } 70% { box-shadow: 0 0 0 6px rgba(31,184,119,0); } 100% { box-shadow: 0 0 0 0 rgba(31,184,119,0); } }
.hero-sub-row { display: flex; align-items: center; gap: 10px; margin-top: 18px; }
.sub-line { width: 18px; height: 1px; background: rgba(255,255,255,0.4); }
.hero-sub { font-size: 14px; font-weight: 500; color: rgba(255,255,255,0.78); letter-spacing: 0.8px; }

/* 主内容圆角浮层容器 */
.content-wrap {
	position: relative;
	flex: 1;
	display: flex;
	margin: -22px 14px 18px;
	background: #ffffff;
	border: 1px solid rgba(255,255,255,0.9);
	border-radius: 22px;
	box-shadow: 0 12px 32px rgba(12,23,51,0.10), 0 2px 6px rgba(12,23,51,0.05);
	overflow: hidden;
}

/* Content */
.content { flex: 1; display: flex; flex-direction: column; padding: 18px 16px 20px; }

.loading-block { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 70px 20px; gap: 14px; }
.loading-text { font-size: 13px; color: var(--ds-ink-3); }

/* 未绑定卡 — 内容水平+垂直居中，按钮固定贴底 */
.unbound-card {
	flex: 1;
	display: flex;
	flex-direction: column;
	background: transparent;
	padding: 24px 18px;
	text-align: center;
	border: none;
}
/* 中部主体：图标+标题+描述 整体水平垂直居中 */
.unbound-body {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 14px;
}
.unbound-ico {
	width: 84px; height: 84px;
	border-radius: 24px;
	background: var(--ds-brand-soft);
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}
.unbound-title { display: block; font-size: 22px; font-weight: 800; color: var(--ds-ink-1); }
.unbound-desc { display: block; font-size: 15px; line-height: 1.7; color: var(--ds-ink-3); max-width: 280px; }
/* 按钮：贴在 unbound-card 底部 */
.unbound-card .primary-btn { width: 100%; flex-shrink: 0; }
.primary-btn { height: 48px; border-radius: var(--ds-r-sm); background: var(--ds-brand); display: flex; align-items: center; justify-content: center; transition: transform 0.18s var(--ds-ease), opacity 0.18s; }
.primary-btn:active, .btn-pressed { transform: scale(0.97); opacity: 0.9; }
.btn-text { font-size: 16px; font-weight: 600; color: #fff; letter-spacing: 0.5px; }

/* 患者卡 */
.patient-card { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 18px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.patient-top { display: flex; align-items: center; gap: 14px; }
.patient-avatar { width: 56px; height: 56px; border-radius: 16px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; box-shadow: var(--ds-shadow-brand); flex-shrink: 0; }
.avatar-text { color: #fff; font-size: 22px; font-weight: 800; }
.patient-main { flex: 1; min-width: 0; }
.patient-name { display: block; font-size: 19px; font-weight: 800; color: var(--ds-ink-1); }
.patient-meta { display: block; margin-top: 4px; font-size: 12px; color: var(--ds-ink-3); }
.relation-tag { padding: 5px 12px; border-radius: var(--ds-r-pill); background: var(--ds-cyan-soft); flex-shrink: 0; }
.relation-tag text { font-size: 11px; font-weight: 700; color: #008695; letter-spacing: 0.3px; }
.patient-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px; }
.patient-info-item { background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 12px; }
.info-label { display: block; font-size: 10px; color: var(--ds-ink-4); margin-bottom: 6px; letter-spacing: 0.8px; }
.info-value { display: block; font-size: 13px; font-weight: 600; color: var(--ds-ink-1); word-break: break-all; }

/* 快捷入口 */
.quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px; }
.quick-card { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 16px 14px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); transition: transform 0.18s var(--ds-ease); }
.quick-card:active, .quick-card.item-pressed { transform: scale(0.985); }
.quick-icon-box { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.quick-icon-box.brand { background: var(--ds-grad-brand);  }
.quick-icon-box.cyan { background: var(--ds-grad-cyan);  }
.quick-icon-box.success { background: linear-gradient(135deg, #1FB877 0%, #00C2D7 100%);  }
.quick-icon-box.warning { background: linear-gradient(135deg, #F5A623 0%, #FF7A59 100%); box-shadow: 0 4px 12px rgba(245,166,35,0.25); }
.quick-title { display: block; font-size: 14px; font-weight: 700; color: var(--ds-ink-1); margin-bottom: 3px; }
.quick-desc { display: block; font-size: 11px; color: var(--ds-ink-3); }

/* Section */
.section { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 18px; margin-top: 14px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.section-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; gap: 12px; }
.section-title { display: block; font-size: 17px; font-weight: 800; color: var(--ds-ink-1); }
.section-sub { display: block; font-size: 10px; color: var(--ds-ink-4); letter-spacing: 1px; margin-top: 4px; }
.section-count { font-size: 11px; font-weight: 600; color: var(--ds-brand); padding: 4px 10px; background: var(--ds-brand-soft); border-radius: var(--ds-r-pill); flex-shrink: 0; }

/* 空 */
.empty-block { padding: 28px 14px; text-align: center; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); }
.empty-ico { width: 52px; height: 52px; border-radius: 50%; background: var(--ds-surface); display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; }
.empty-title { display: block; font-size: 14px; font-weight: 700; color: var(--ds-ink-2); margin-bottom: 4px; }
.empty-desc { display: block; font-size: 12px; color: var(--ds-ink-4); line-height: 1.55; }

/* Record */
.record-card { background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 14px; margin-bottom: 10px; transition: background 0.18s, transform 0.18s; }
.record-card:last-child { margin-bottom: 0; }
.record-card:active, .record-card.item-pressed { transform: scale(0.99); background: var(--ds-surface); box-shadow: var(--ds-shadow-md); }
.record-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 8px; }
.record-title { font-size: 14px; font-weight: 700; color: var(--ds-ink-1); flex: 1; min-width: 0; }
.record-status { padding: 3px 9px; border-radius: var(--ds-r-pill); flex-shrink: 0; background: var(--ds-bg-sunken); }
.record-status text { font-size: 10px; font-weight: 700; color: var(--ds-ink-3); letter-spacing: 0.3px; }
.record-status.status-accepted, .record-status.status-processing { background: var(--ds-brand-soft); }
.record-status.status-accepted text, .record-status.status-processing text { color: var(--ds-brand); }
.record-status.status-completed { background: rgba(31,184,119,0.13); }
.record-status.status-completed text { color: var(--ds-success); }
.record-status.status-rejected { background: rgba(255,77,94,0.13); }
.record-status.status-rejected text { color: var(--ds-danger); }
.record-status.status-cancelled { background: var(--ds-bg-sunken); }
.record-time { display: block; font-size: 11px; color: var(--ds-ink-4); letter-spacing: 0.3px; }
.record-info { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--ds-ink-3); margin-top: 8px; }
.record-diagnosis { display: block; margin-top: 9px; font-size: 12px; line-height: 1.6; color: var(--ds-ink-2); }
.record-action { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--ds-hairline); display: flex; align-items: center; justify-content: flex-end; gap: 4px; }
.record-action-text { font-size: 12px; font-weight: 600; color: var(--ds-brand); }
.record-action-arrow { font-size: 16px; color: var(--ds-brand); line-height: 1; }
.reject-reason { color: var(--ds-danger); }
</style>
