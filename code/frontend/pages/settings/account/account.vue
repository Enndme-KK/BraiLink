<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack" hover-class="back-pressed">
					<text class="back-char">‹</text>
				</view>
				<text class="nav-title">账号管理</text>
				<view class="nav-placeholder"></view>
			</view>
		</view>

		<view class="content">
			<view class="list-group ds-rise ds-d1">
				<view class="list-item" @click="open(1)" hover-class="item-pressed">
					<text class="item-label">姓名</text>
					<text class="item-value">{{ accountForm.name || '未设置' }}</text>
					<text class="item-chevron">›</text>
				</view>
				<view class="list-item" v-if="userType === 'patient'" @click="open(2)" hover-class="item-pressed">
					<text class="item-label">身份证</text>
					<text class="item-value">{{ accountForm.card_num || '未设置' }}</text>
					<text class="item-chevron">›</text>
				</view>
				<view class="list-item" v-if="userType === 'doctor'" @click="open(2)" hover-class="item-pressed">
					<text class="item-label">执业证号</text>
					<text class="item-value">{{ accountForm.license_number || '未设置' }}</text>
					<text class="item-chevron">›</text>
				</view>
				<view class="list-item" @click="open(3)" hover-class="item-pressed">
					<text class="item-label">绑定手机号</text>
					<text class="item-value">{{ accountForm.phone || '未设置' }}</text>
					<text class="item-chevron">›</text>
				</view>
				<view class="list-item" v-if="userType === 'patient'" @click="open(4)" hover-class="item-pressed">
					<text class="item-label">联系地址</text>
					<text class="item-value">{{ accountForm.loc || '未设置' }}</text>
					<text class="item-chevron">›</text>
				</view>
				<view class="list-item" v-if="userType === 'doctor'" @click="open(5)" hover-class="item-pressed">
					<text class="item-label">所属医院</text>
					<text class="item-value">{{ accountForm.hospital || '未设置' }}</text>
					<text class="item-chevron">›</text>
				</view>
				<view class="list-item" v-if="userType === 'doctor'" @click="open(6)" hover-class="item-pressed">
					<text class="item-label">所属科室</text>
					<text class="item-value">{{ accountForm.department || '未设置' }}</text>
					<text class="item-chevron">›</text>
				</view>
			</view>
		</view>

		<uni-popup ref="popup" type="center">
			<view class="popup-card">
				<text class="popup-title">{{ getPopupTitle() }}</text>
				<view class="popup-input-box">
					<textarea class="popup-input" :placeholder="getPlaceholder()" placeholder-class="ph" v-model="currentValue" maxlength="200" @input="countCharacters" />
					<text class="popup-counter ds-mono">{{ characterCount }} / 200</text>
				</view>
				<view class="popup-actions">
					<view class="popup-btn ghost" @click="cancel"><text>取消</text></view>
					<view class="popup-btn primary" @click="confirm"><text>确认</text></view>
				</view>
			</view>
		</uni-popup>
	</view>
</template>

<script>
import uniPopup from '@/uni_modules/uni-popup/components/uni-popup/uni-popup.vue'
import { patientAPI, doctorAPI, authAPI } from '@/utils/request.js'

export default {
	components: { uniPopup },
	data() {
		return {
			userType: 'patient',
			accountForm: { name: '', card_num: '', license_number: '', phone: '', loc: '', hospital: '', department: '' },
			characterCount: 0, changeIdx: 0, currentValue: '', loading: false
		}
	},
	async onLoad() { await this.getUserType(); this.loadAccountInfo() },
	methods: {
		goBack() { uni.navigateBack({ delta: 1 }) },
		async getUserType() {
			try {
				const user = uni.getStorageSync('user')
				if (user && user.user_type) this.userType = user.user_type
				else {
					const r = await authAPI.getProfile()
					if (r && r.user_type) { this.userType = r.user_type; uni.setStorageSync('user', r) }
				}
			} catch (e) {}
		},
		async loadAccountInfo() {
			try {
				this.loading = true
				if (this.userType === 'patient') {
					const r = await patientAPI.getMyProfile()
					if (r) this.accountForm = { name: r.name || '', card_num: r.id_card || '', phone: r.phone || '', loc: r.address || '', license_number: '', hospital: '', department: '' }
				} else if (this.userType === 'doctor') {
					const r = await doctorAPI.getMyProfile()
					if (r) this.accountForm = { name: r.name || r.user?.name || '', license_number: r.license_number || '', phone: r.phone || r.user?.phone || '', hospital: r.hospital || '', department: r.department || '', card_num: '', loc: '' }
				}
			} catch (e) {
				try {
					const r = await authAPI.getProfile()
					if (r) { this.accountForm.name = r.name || ''; this.accountForm.phone = r.phone || '' }
				} catch (e2) {}
			} finally { this.loading = false }
		},
		getFieldKey() {
			return ['', 'name', this.userType === 'patient' ? 'card_num' : 'license_number', 'phone', 'loc', 'hospital', 'department'][this.changeIdx]
		},
		getPopupTitle() {
			return ['', '修改姓名', this.userType === 'patient' ? '修改身份证' : '修改执业证号', '修改手机号', '修改地址', '修改医院', '修改科室'][this.changeIdx]
		},
		getPlaceholder() {
			return ['', '请输入姓名', this.userType === 'patient' ? '请输入身份证号' : '请输入执业证号', '请输入手机号', '请输入地址', '请输入医院名称', '请输入科室名称'][this.changeIdx]
		},
		open(index) {
			this.changeIdx = index
			this.currentValue = this.accountForm[this.getFieldKey()] || ''
			this.characterCount = this.currentValue.length
			this.$refs.popup.open()
		},
		cancel() { this.$refs.popup.close() },
		countCharacters() { this.characterCount = this.currentValue.length },
		async confirm() {
			try {
				uni.showLoading({ title: '保存中...' })
				this.accountForm[this.getFieldKey()] = this.currentValue
				if (this.userType === 'patient') {
					const id = await this.getPatientId()
					if (id) await patientAPI.updateProfile(id, { name: this.accountForm.name, id_card: this.accountForm.card_num, phone: this.accountForm.phone, address: this.accountForm.loc })
				} else if (this.userType === 'doctor') {
					const id = await this.getDoctorId()
					if (id) await doctorAPI.updateProfile(id, {
						name: this.accountForm.name,
						license_number: this.accountForm.license_number,
						phone: this.accountForm.phone,
						hospital: this.accountForm.hospital,
						department: this.accountForm.department
					})
				}
				uni.hideLoading()
				this.$refs.popup.close()
				uni.showToast({ title: '保存成功', icon: 'success' })
				this.loadAccountInfo()
			} catch (e) {
				uni.hideLoading()
				const msg = (e && e.response && e.response.data && (e.response.data.error || e.response.data.detail)) || e.message || '保存失败'
				uni.showToast({ title: msg, icon: 'none', duration: 2500 })
			}
		},
		async getPatientId() {
			try { const r = await patientAPI.getMyProfile(); return r.id } catch (e) { return null }
		},
		async getDoctorId() {
			try { const r = await doctorAPI.getMyProfile(); return r.id } catch (e) { return null }
		}
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); font-family: var(--ds-font); }
.navbar { position: sticky; top: 0; z-index: 100; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.82); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-inner { position: relative; display: flex; align-items: center; justify-content: space-between; padding: 52px 16px 12px; }
.nav-back { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
.back-pressed { background: var(--ds-brand-ghost); }
.back-char { font-size: 32px; font-weight: 300; color: var(--ds-brand); line-height: 1; margin-top: -4px; }
.nav-title { font-size: 17px; font-weight: 600; color: var(--ds-ink-1); }
.nav-placeholder { width: 36px; }

.content { padding: 18px 20px 30px; }
.list-group { background: var(--ds-surface); border-radius: var(--ds-r-md); overflow: hidden; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); }
.list-item { display: flex; align-items: center; padding: 14px 16px; gap: 14px; transition: background 0.15s; min-height: 22px; }
.list-item + .list-item { border-top: 1px solid var(--ds-hairline); }
.item-pressed { background: var(--ds-bg-sunken); }
.item-label { font-size: 15px; font-weight: 600; color: var(--ds-ink-1); flex-shrink: 0; min-width: 92px; }
.item-value { flex: 1; font-size: 14px; color: var(--ds-ink-3); text-align: right; word-break: break-all; }
.item-chevron { font-size: 22px; font-weight: 300; color: var(--ds-ink-4); flex-shrink: 0; }

/* Popup */
.popup-card { width: 320px; background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 20px; box-shadow: var(--ds-shadow-lg); }
.popup-title { display: block; font-size: 16px; font-weight: 700; color: var(--ds-ink-1); margin-bottom: 14px; }
.popup-input-box { background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); padding: 12px; margin-bottom: 16px; }
.popup-input { width: 100%; min-height: 80px; font-size: 14px; line-height: 1.5; color: var(--ds-ink-1); background: transparent; border: none; }
.ph { color: var(--ds-ink-4); }
.popup-counter { display: block; text-align: right; font-size: 11px; color: var(--ds-ink-4); margin-top: 6px; }
.popup-actions { display: flex; gap: 10px; }
.popup-btn { flex: 1; height: 44px; border-radius: var(--ds-r-sm); display: flex; align-items: center; justify-content: center; transition: opacity 0.18s, transform 0.18s; }
.popup-btn:active { transform: scale(0.97); }
.popup-btn.ghost { background: var(--ds-bg-sunken); }
.popup-btn.ghost text { font-size: 15px; color: var(--ds-ink-2); font-weight: 600; }
.popup-btn.primary { background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); }
.popup-btn.primary text { font-size: 15px; color: #fff; font-weight: 600; }
</style>
