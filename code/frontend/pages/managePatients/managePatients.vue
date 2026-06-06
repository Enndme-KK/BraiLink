<template>
	<view class="page">
		<view class="navbar" :style="{ opacity: navOpacity }">
			<view class="navbar-bg" :style="{ opacity: navBgOpacity }"></view>
			<view class="navbar-content">
				<text class="navbar-title">患者管理</text>
			</view>
		</view>

		<view class="large-title-area">
			<text class="large-title">患者管理</text>
		</view>

		<view class="search-area">
			<view class="search-bar">
				<text class="search-icon-text">S</text>
				<input class="search-input" v-model="searchTxt" placeholder="搜索患者姓名或ID" placeholder-class="ph" @confirm="getPatientByName" />
				<view class="search-action" @click="getPatientByName" v-if="searchTxt"><text class="action-text">搜索</text></view>
				<view class="search-clear" @click="clearSearch" v-if="searchTxt"><text class="clear-text">✕</text></view>
			</view>
		</view>

		<view class="content">
			<!-- 统计 -->
			<view class="stats-row">
				<view class="stat-card" v-for="(s, i) in statCards" :key="i">
					<text class="stat-num">{{ s.value }}</text>
					<text class="stat-label">{{ s.label }}</text>
				</view>
			</view>

			<!-- 待接诊 -->
			<view class="section-card" v-if="pendingAppointments.length > 0 || appointmentLoading">
				<view class="section-head">
					<text class="section-title">待接诊挂号</text>
					<view class="refresh-btn" @click="loadPendingAppointments"><text class="refresh-text">刷新</text></view>
				</view>
				<view class="appt-loading" v-if="appointmentLoading"><text class="appt-hint">加载中...</text></view>
				<block v-else>
					<view class="appt-item" v-for="item in pendingAppointments" :key="item.id">
						<view class="appt-row">
							<view class="appt-avatar"><text class="appt-avatar-text">{{ getNameInitial(item.patient_name) }}</text></view>
							<view class="appt-info">
								<view class="appt-name-row">
									<text class="appt-name">{{ item.patient_name || '未知患者' }}</text>
									<view class="appt-type-tag"><text class="appt-type-text">{{ item.appointment_type_display || getAppointmentTypeText(item.appointment_type) }}</text></view>
								</view>
								<text class="appt-detail">{{ formatDate(item.visit_date) }} · {{ item.department || '未填写' }}</text>
								<text class="appt-detail">主诉：{{ item.symptoms || '暂无' }}</text>
							</view>
						</view>
						<view class="appt-actions">
							<view class="btn-secondary" :class="{ disabled: handlingAppointmentId === item.id }" @click.stop="rejectAppointment(item)"><text class="btn-secondary-text">拒绝</text></view>
							<view class="btn-primary-sm" :class="{ disabled: handlingAppointmentId === item.id }" @click.stop="acceptAppointment(item)"><text class="btn-primary-text">{{ handlingAppointmentId === item.id ? '处理中' : '接诊' }}</text></view>
						</view>
					</view>
				</block>
			</view>

			<!-- 患者列表 -->
			<text class="group-label" v-if="patients.length > 0">全部患者</text>
			<view class="loading-state" v-if="loading"><view class="spinner"></view></view>
			<view class="empty-state" v-else-if="patients.length === 0 && !appointmentLoading"><text class="empty-text">暂无患者信息</text></view>

			<view class="list-group" v-if="patients.length > 0">
				<view class="list-item" v-for="(patient, index) in patients" :key="patient.pat_id" @click="toPatientReportPage(patient)" hover-class="item-pressed">
					<view class="item-avatar-wrap">
						<image :src="patient.gender == 1 ? '/static/resource/boy.png' : '/static/resource/girl.png'" class="item-avatar" mode="aspectFill" />
						<view class="status-dot" :class="getStatusClass(patient)"></view>
					</view>
					<view class="item-body">
						<view class="item-title-row">
							<text class="item-title">{{ patient.name }}</text>
							<view class="gender-tag" :class="patient.gender == 1 ? 'male' : 'female'">
								<text class="gender-char">{{ patient.gender == 1 ? '♂' : '♀' }}</text>
							</view>
							<view class="family-tag" :class="patient.has_family ? 'has-family' : 'no-family'">
								<text class="family-tag-text">{{ patient.has_family ? '有家属' : '无家属' }}</text>
							</view>
						</view>
						<text class="item-sub">{{ patient.presentation || '暂无主诉' }}</text>
						<text class="item-time">{{ formatDate(patient.check_time) }}</text>
					</view>
					<view class="msg-btn" @click.stop="toChat(patient)" hover-class="msg-btn-pressed">
						<text class="msg-btn-icon">✉</text>
					</view>
					<view class="item-chevron"><text class="chevron-char">›</text></view>
				</view>
			</view>

			<!-- 关联家属 -->
			<text class="group-label" v-if="families.length > 0">关联家属</text>
			<view class="list-group" v-if="families.length > 0">
				<view class="list-item" v-for="f in families" :key="f.family_user_id" hover-class="item-pressed">
					<view class="item-avatar-wrap">
						<view class="family-avatar"><text class="family-avatar-text">{{ f.family_name ? f.family_name.slice(0,1) : '家' }}</text></view>
					</view>
					<view class="item-body">
						<view class="item-title-row">
							<text class="item-title">{{ f.family_name }}</text>
							<view class="gender-tag male" v-if="f.relationship"><text class="gender-char" style="color:var(--ds-cyan)">{{ f.relationship }}</text></view>
						</view>
						<text class="item-sub">患者：{{ f.patient_name }}</text>
					</view>
					<view class="msg-btn" @click.stop="toChatFamily(f)" hover-class="msg-btn-pressed">
						<text class="msg-btn-icon">✉</text>
					</view>
				</view>
			</view>

			<view style="height: 100px;"></view>
		</view>

		<bottom-nav-doctor current="patients"></bottom-nav-doctor>
	</view>
</template>

<script>
import BottomNavDoctor from '@/components/bottom_nav/BottomNavDoctor.vue'
import { appointmentAPI, patientAPI, doctorAPI } from '@/utils/request.js'

export default {
	name: 'managePatients',
	components: { BottomNavDoctor },
	onLoad() {
		import('@/utils/auth.js').then(m => {
			if (!m.requireAuth()) return
			if (m.getCurrentUserType() !== 'doctor') { uni.showToast({ title: '此页面仅限医生访问', icon: 'none' }); setTimeout(() => uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' }), 1500); return }
			this.getPatientsList(); this.loadPendingAppointments(); this.loadFamilies()
		})
	},
	onShow() { const u = uni.getStorageSync('user'); if (u?.user_type === 'doctor') { this.loadPendingAppointments(); this.getPatientsList() } },
	onPageScroll(e) { this.scrollY = e.scrollTop },
	data() { return { scrollY: 0, patients: [], allPatients: [], pendingAppointments: [], appointmentLoading: false, handlingAppointmentId: null, searchTxt: '', loading: false, families: [], familiesLoading: false } },
	computed: {
		navOpacity() { return Math.min(this.scrollY / 100, 1) },
		navBgOpacity() { return Math.min(this.scrollY / 100, 0.85) },
		statCards() { return [{ value: this.patients.length, label: '总患者数' }, { value: this.getTodayCount(), label: '今日新增' }, { value: this.pendingAppointments.length, label: '待接诊' }] }
	},
	methods: {
		async loadPendingAppointments() { this.appointmentLoading = true; try { const r = await appointmentAPI.getDoctorPending(); this.pendingAppointments = Array.isArray(r) ? r : (r.results || []) } catch(e) { this.pendingAppointments = [] } finally { this.appointmentLoading = false } },
		acceptAppointment(item) { if (!item || this.handlingAppointmentId) return; uni.showModal({ title: '确认接诊', content: `确认接诊 ${item.patient_name || '未知患者'} 吗？`, success: async r => { if (r.confirm) { this.handlingAppointmentId = item.id; try { await appointmentAPI.acceptAppointment(item.id); uni.showToast({ title: '已接诊', icon: 'success' }); await this.loadPendingAppointments(); await this.getPatientsList() } catch(e) { uni.showToast({ title: e?.response?.data?.error || e.message || '接诊失败', icon: 'none' }) } finally { this.handlingAppointmentId = null } } } }) },
		rejectAppointment(item) { if (!item || this.handlingAppointmentId) return; uni.showModal({ title: '拒绝挂号', editable: true, placeholderText: '拒绝原因（可留空）', success: async r => { if (r.confirm) { this.handlingAppointmentId = item.id; try { await appointmentAPI.rejectAppointment(item.id, { reason: (r.content || '').trim() }); uni.showToast({ title: '已拒绝', icon: 'success' }); await this.loadPendingAppointments() } catch(e) { uni.showToast({ title: e?.response?.data?.error || e.message || '操作失败', icon: 'none' }) } finally { this.handlingAppointmentId = null } } } }) },
		getNameInitial(n) { return n ? String(n).slice(0,1) : '患' },
		getAppointmentTypeText(t) { return { outpatient: '门诊', expert: '专家', emergency: '急诊', followup: '复诊' }[t] || t || '挂号' },
		async getPatientsList() { this.loading = true; try { const r = await patientAPI.getPatients(); const data = Array.isArray(r) ? r : (r?.results || []); this.allPatients = data.map(p => ({ pat_id: String(p.id || '') || p.id_card || '', name: p.name || '未知', gender: p.gender === 'M' ? 1 : 2, age: p.age || 0, phone: p.phone || '', presentation: p.medical_history?.trim() || '暂无主诉', check_time: p.created_at || '', has_family: !!p.has_family, _raw: p })); this.patients = this.allPatients } catch(e) { this.allPatients = []; this.patients = [] } finally { this.loading = false } },
		toPatientReportPage(p) { uni.navigateTo({ url: '/pages/ctReport/ctReport?pat_id=' + (p._raw?.id || p.pat_id || p.card_id) }) },
		getPatientByName() { if (!this.searchTxt.trim()) { this.patients = this.allPatients; return }; const kw = this.searchTxt.toLowerCase().trim(); this.patients = this.allPatients.filter(p => (p.name||'').toLowerCase().includes(kw) || (p.pat_id||'').toLowerCase().includes(kw) || (p.phone||'').toLowerCase().includes(kw)); if (!this.patients.length) uni.showToast({ title: '未找到', icon: 'none' }) },
		clearSearch() { this.searchTxt = ''; this.getPatientsList() },
		formatDate(d) { if (!d) return ''; const dt = new Date(d); return isNaN(dt.getTime()) ? d : `${dt.getMonth()+1}月${dt.getDate()}日 ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}` },
		getTodayCount() { const t = new Date().toDateString(); return this.patients.filter(p => p.check_time && new Date(p.check_time).toDateString() === t).length },
		toChat(patient) { const u = patient._raw?.user; const userId = (u && typeof u === 'object' ? u.id : u) || patient._raw?.user_id || ''; if (!userId) { uni.showToast({ title: '该患者未关联用户账户', icon: 'none' }); return } uni.navigateTo({ url: `/pages/chat/chatDialog?partner_id=${userId}&partner_role=patient&partner_name=${encodeURIComponent(patient.name || '')}` }) },
		toChatFamily(family) { const fid = family.family_user_id || ''; if (!fid) { uni.showToast({ title: '家属信息不完整', icon: 'none' }); return } uni.navigateTo({ url: `/pages/chat/chatDialog?partner_id=${fid}&partner_role=family&partner_name=${encodeURIComponent(family.family_name || '')}` }) },
		async loadFamilies() { this.familiesLoading = true; try { const r = await doctorAPI.getRelatedFamilies(); this.families = Array.isArray(r) ? r : [] } catch(e) { this.families = [] } finally { this.familiesLoading = false } },
		getStatusClass(p) { if (!p.check_time) return 'inactive'; const d = (Date.now() - new Date(p.check_time)) / 86400000; return d < 7 ? 'active' : d < 30 ? 'warning' : 'inactive' }
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); font-family: var(--ds-font); padding-bottom: 80px; }

.navbar { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; opacity: 0; transition: opacity 0.18s var(--ds-ease); pointer-events: none; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-content { position: relative; padding: 52px 20px 12px; text-align: center; }
.navbar-title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); letter-spacing: 0.5px; }

.large-title-area { padding: 54px 20px 0; }
.large-title { font-size: 32px; font-weight: 800; color: var(--ds-ink-1); letter-spacing: -0.5px; }

.search-area { padding: 14px 20px 0; }
.search-bar { display: flex; align-items: center; gap: 8px; background: var(--ds-surface); border: 1px solid var(--ds-hairline); border-radius: var(--ds-r-sm); padding: 0 12px; height: 40px; box-shadow: var(--ds-shadow-sm); }
.search-icon-text { font-size: 14px; font-weight: 800; color: var(--ds-ink-3); margin-right: 4px; }
.search-input { flex: 1; font-size: 15px; color: var(--ds-ink-1); background: transparent; border: none; height: 40px; }
.ph { color: var(--ds-ink-4); }
.search-action { padding: 6px 14px; border-radius: var(--ds-r-pill); background: var(--ds-grad-brand); margin-left: 4px; box-shadow: var(--ds-shadow-brand); }
.action-text { font-size: 13px; color: #fff; font-weight: 600; }
.search-clear { width: 18px; height: 18px; border-radius: 50%; background: var(--ds-bg-sunken); display: flex; align-items: center; justify-content: center; }
.clear-text { font-size: 10px; color: var(--ds-ink-3); }

.content { padding: 16px 20px 0; }

.stats-row { display: flex; gap: 10px; margin-bottom: 16px; }
.stat-card { flex: 1; background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 16px; text-align: center; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.stat-num { display: block; font-size: 26px; font-weight: 800; color: var(--ds-brand); margin-bottom: 4px; letter-spacing: -0.5px; }
.stat-label { display: block; font-size: 11px; color: var(--ds-ink-3); }

.section-card { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 16px; margin-bottom: 16px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.section-title { font-size: 16px; font-weight: 800; color: var(--ds-ink-1); }
.refresh-btn { padding: 6px 12px; border-radius: var(--ds-r-pill); background: var(--ds-brand-soft); }
.refresh-text { font-size: 12px; color: var(--ds-brand); font-weight: 600; }
.appt-loading { padding: 16px; text-align: center; }
.appt-hint { font-size: 13px; color: var(--ds-ink-3); }
.appt-item { padding: 14px 0; }
.appt-item + .appt-item { border-top: 1px solid var(--ds-hairline); }
.appt-row { display: flex; gap: 12px; margin-bottom: 10px; }
.appt-avatar { width: 42px; height: 42px; border-radius: 12px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; flex-shrink: 0;  }
.appt-avatar-text { font-size: 16px; font-weight: 800; color: #fff; }
.appt-info { flex: 1; min-width: 0; }
.appt-name-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.appt-name { font-size: 15px; font-weight: 700; color: var(--ds-ink-1); }
.appt-type-tag { padding: 2px 8px; border-radius: var(--ds-r-pill); background: var(--ds-cyan-soft); }
.appt-type-text { font-size: 10px; color: #008695; font-weight: 700; letter-spacing: 0.3px; }
.appt-detail { display: block; font-size: 12px; color: var(--ds-ink-3); line-height: 1.55; }
.appt-actions { display: flex; justify-content: flex-end; gap: 8px; }
.btn-secondary { min-width: 64px; height: 32px; border-radius: var(--ds-r-pill); background: rgba(255,77,94,0.1); display: flex; align-items: center; justify-content: center; padding: 0 14px; transition: background 0.18s; }
.btn-secondary:active { background: rgba(255,77,94,0.18); }
.btn-secondary.disabled { opacity: 0.4; }
.btn-secondary-text { font-size: 13px; font-weight: 600; color: var(--ds-danger); }
.btn-primary-sm { min-width: 64px; height: 32px; border-radius: var(--ds-r-pill); background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); display: flex; align-items: center; justify-content: center; padding: 0 14px; transition: transform 0.18s; }
.btn-primary-sm:active { transform: scale(0.96); }
.btn-primary-sm.disabled { opacity: 0.4; }
.btn-primary-text { font-size: 13px; font-weight: 600; color: #fff; }

.group-label { display: block; font-size: 11px; font-weight: 700; color: var(--ds-ink-4); text-transform: uppercase; letter-spacing: 1px; margin: 8px 0 10px; padding-left: 4px; font-family: var(--ds-font-mono); }

.list-group { background: var(--ds-surface); border-radius: var(--ds-r-md); overflow: hidden; margin-bottom: 16px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.list-item { display: flex; align-items: center; padding: 14px 16px; gap: 12px; transition: background 0.15s; }
.list-item + .list-item { border-top: 1px solid var(--ds-hairline); }
.item-pressed { background: var(--ds-bg-sunken); }
.item-avatar-wrap { position: relative; flex-shrink: 0; }
.item-avatar { width: 46px; height: 46px; border-radius: 14px; }
.status-dot { position: absolute; bottom: -2px; right: -2px; width: 12px; height: 12px; border-radius: 50%; border: 2px solid var(--ds-surface); }
.status-dot.active { background: var(--ds-success); }
.status-dot.warning { background: var(--ds-warning); }
.status-dot.inactive { background: var(--ds-ink-4); }
.item-body { flex: 1; min-width: 0; }
.item-title-row { display: flex; align-items: center; gap: 6px; margin-bottom: 3px; }
.item-title { font-size: 15px; font-weight: 700; color: var(--ds-ink-1); }
.gender-tag { padding: 1px 6px; border-radius: 6px; }
.gender-tag.male { background: var(--ds-brand-soft); }
.gender-tag.female { background: rgba(255,77,94,0.13); }
.gender-char { font-size: 12px; font-weight: 700; }
.gender-tag.male .gender-char { color: var(--ds-brand); }
.gender-tag.female .gender-char { color: var(--ds-danger); }
.family-tag { padding: 1px 6px; border-radius: 6px; }
.family-tag.has-family { background: rgba(31,184,119,0.12); }
.family-tag.no-family { background: var(--ds-bg-sunken); }
.family-tag-text { font-size: 10px; font-weight: 700; }
.family-tag.has-family .family-tag-text { color: #1FB877; }
.family-tag.no-family .family-tag-text { color: var(--ds-ink-4); }
.item-sub { display: block; font-size: 13px; color: var(--ds-ink-3); margin-bottom: 3px; -webkit-line-clamp: 1; overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; }
.item-time { font-size: 11px; color: var(--ds-ink-4); font-family: var(--ds-font-mono); letter-spacing: 0.3px; }
.item-chevron { flex-shrink: 0; }
.chevron-char { font-size: 22px; font-weight: 300; color: var(--ds-ink-4); }
.msg-btn { width: 32px; height: 32px; border-radius: 10px; background: var(--ds-brand-soft); display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: background 0.18s; }
.msg-btn-pressed { background: var(--ds-brand-ghost); }
.msg-btn-icon { font-size: 14px; color: var(--ds-brand); }
.family-avatar { width: 46px; height: 46px; border-radius: 14px; background: linear-gradient(135deg, #F5A623 0%, #FF7A59 100%); display: flex; align-items: center; justify-content: center; }
.family-avatar-text { font-size: 18px; font-weight: 700; color: #fff; }

.loading-state { padding: 40px 0; display: flex; justify-content: center; }
.spinner { width: 22px; height: 22px; border: 2px solid var(--ds-hairline); border-top-color: var(--ds-brand); border-radius: 50%; animation: spin 0.7s linear infinite; }
.empty-state { padding: 60px 20px; text-align: center; }
.empty-text { font-size: 14px; color: var(--ds-ink-4); }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
