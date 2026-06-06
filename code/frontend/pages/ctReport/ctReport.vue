<template>
	<view class="page">
		<!-- 导航栏 -->
		<view class="navbar">
			<view class="navbar-inner">
				<view class="navbar-left" @click="toManagePage">
					<view class="back-arrow"></view>
				</view>
				<view class="navbar-center">
					<text class="navbar-title">患者病历记录</text>
					<text class="navbar-sub">Medical Records</text>
				</view>
				<view class="navbar-right"></view>
			</view>
		</view>

		<scroll-view scroll-y class="scroll-area" :style="{ height: scrollHeight, overflowX: 'hidden' }">
			<!-- ===== 病历列表视图 ===== -->
			<block v-if="showRecordsList">
				<!-- 联系家属 -->
				<view class="family-contact-section" v-if="familiesLoaded">
					<view class="family-contact-card" v-if="patientFamilies.length > 0">
						<text class="family-contact-title has-family-title">联系家属</text>
						<view class="family-item" v-for="f in patientFamilies" :key="f.family_user_id">
							<view class="family-avatar-sm"><text class="family-avatar-sm-text">{{ f.family_name.slice(0,1) }}</text></view>
							<view class="family-info">
								<text class="family-name">{{ f.family_name }}</text>
								<text class="family-rel" v-if="f.relationship">{{ f.relationship }}</text>
							</view>
							<view class="family-msg-btn" @click="toChatFamily(f)" hover-class="family-msg-pressed">
								<text class="family-msg-icon">✉</text>
								<text class="family-msg-text">发消息</text>
							</view>
						</view>
					</view>
					<view class="family-empty-card" v-else @click="goToFamilyBind" hover-class="family-empty-pressed">
						<text class="family-empty-icon">👨‍👩‍👧</text>
						<text class="family-empty-text">联系家属</text>
						<text class="family-empty-sub">该患者暂未绑定家属，点击前往绑定</text>
					</view>
				</view>

				<!-- 患者信息卡片 -->
				<view class="patient-card" v-if="patient.name">
					<view class="patient-avatar">
						<image :src="patient.gender === '男' ? '/static/resource/boy.png' : '/static/resource/girl.png'" class="avatar-img" mode="aspectFill"></image>
					</view>
					<view class="patient-info">
						<text class="patient-name">{{ patient.name || '未知患者' }}</text>
						<view class="patient-meta">
							<view class="meta-tag">
								<text class="meta-label">性别</text>
								<text class="meta-value">{{ patient.gender || '未知' }}</text>
							</view>
							<view class="meta-tag">
								<text class="meta-label">年龄</text>
								<text class="meta-value">{{ patient.age }}岁</text>
							</view>
							<view class="meta-tag">
								<text class="meta-label">病历号</text>
								<text class="meta-value">{{ patient.pat_id || '暂无' }}</text>
							</view>
						</view>
					</view>
				</view>

				<!-- 记录列表 -->
				<view class="records-section">
					<view class="records-header">
						<text class="records-title">就诊记录</text>
						<view class="records-actions">
							<text class="records-count">共 {{ medicalRecords.length }} 条</text>
							<view class="add-btn" @click="showAddRecordForm">
								<text class="add-btn-text">+ 添加</text>
							</view>
						</view>
					</view>

					<!-- 加载中 -->
					<view class="loading-state" v-if="loading">
						<view class="loading-spinner"></view>
						<text class="loading-text">加载中...</text>
					</view>

					<!-- 空状态 -->
					<view class="empty-state" v-else-if="medicalRecords.length === 0">
						<view class="empty-icon-wrap">
							<text class="empty-icon-text">0</text>
						</view>
						<text class="empty-title">暂无就诊记录</text>
						<text class="empty-desc">该患者还没有任何就诊记录</text>
					</view>

					<!-- 记录卡片 -->
					<view
						class="record-card"
						v-for="(record, index) in medicalRecords"
						:key="record.id || index"
						@click="viewRecordDetail(record)"
						:style="{ animationDelay: index * 0.08 + 's' }"
					>
						<view class="record-top">
							<view class="record-date-wrap">
								<text class="record-date">{{ record.check_time }}</text>
								<view class="real-badge" v-if="!record.is_demo">
									<text class="real-badge-text">真实</text>
								</view>
							</view>
							<view class="record-status-tag">
								<text class="status-dot"></text>
								<text class="status-text">已完成</text>
							</view>
						</view>
						<view class="record-body">
							<view class="record-thumb" v-if="record.img_url">
								<image :src="record.img_url" class="thumb-img" mode="aspectFill"></image>
							</view>
							<view class="record-main">
								<text class="record-project">{{ record.check_project }}</text>
								<text class="record-result">{{ record.imaging_finding_result }}</text>
								<text class="record-dept" v-if="record.department">{{ record.department }}</text>
							</view>
							<view class="record-arrow">
								<view class="arrow-icon"></view>
							</view>
						</view>
					</view>
				</view>
			</block>

			<!-- ===== 病历详情视图 ===== -->
			<block v-if="!showRecordsList">
				<!-- 返回按钮 -->
				<view class="back-row">
					<view class="back-pill" @click="backToList">
						<view class="back-arrow-sm"></view>
						<text class="back-pill-text">返回列表</text>
					</view>
				</view>

				<!-- 患者信息卡片 (详情) -->
				<view class="detail-card">
					<text class="detail-card-title">患者信息</text>
					<view class="info-grid">
						<view class="info-cell">
							<text class="info-key">患者号</text>
							<text class="info-val">{{ patient.pat_id }}</text>
						</view>
						<view class="info-cell">
							<text class="info-key">检查日期</text>
							<text class="info-val">{{ patient.check_time }}</text>
						</view>
					</view>
					<view class="info-divider"></view>
					<view class="info-grid info-grid-3">
						<view class="info-cell">
							<text class="info-key">姓名</text>
							<text class="info-val">{{ patient.name }}</text>
						</view>
						<view class="info-cell">
							<text class="info-key">性别</text>
							<text class="info-val">{{ patient.gender }}</text>
						</view>
						<view class="info-cell">
							<text class="info-key">年龄</text>
							<text class="info-val">{{ patient.age }}岁</text>
						</view>
					</view>
					<view class="info-grid">
						<view class="info-cell">
							<text class="info-key">住院号</text>
							<text class="info-val">{{ patient.host_id }}</text>
						</view>
						<view class="info-cell">
							<text class="info-key">科室</text>
							<text class="info-val">{{ patient.department }}</text>
						</view>
						<view class="info-cell">
							<text class="info-key">床号</text>
							<text class="info-val">{{ patient.bed_num }}</text>
						</view>
					</view>
					<view class="info-divider"></view>
					<view class="info-row-single">
						<text class="info-key">报告日期</text>
						<text class="info-val">{{ patient.report_time }}</text>
					</view>
					<view class="info-row-single">
						<text class="info-key">检查项目</text>
						<text class="info-val">{{ patient.check_project }} · {{ patient.position }}</text>
					</view>
				</view>

				<!-- 影像结果 -->
				<view class="detail-card">
					<text class="detail-card-title">影像结果</text>
					<text class="detail-text">{{ imaging_finding_result }}</text>
				</view>

				<!-- 影像诊断 -->
				<view class="detail-card diagnosis-card">
					<view class="diagnosis-bar"></view>
					<view class="diagnosis-inner">
						<text class="diagnosis-title">影像诊断</text>
						<text class="diagnosis-text">{{ imaging_diagnosis_result }}</text>
					</view>
				</view>

				<!-- 原始 MRI 图 -->
				<view class="detail-card" v-if="primeTumorPicList.length > 0">
					<text class="detail-card-title">原始 MRI 图</text>
					<view class="image-grid">
						<view
							class="image-cell"
							v-for="(image, index) in primeTumorPicList"
							:key="'p' + index"
							@click="previewImage(image)"
						>
							<image :src="image" class="cell-img" mode="aspectFill"></image>
						</view>
					</view>
				</view>

				<!-- AI 分割结果 -->
				<view class="detail-card">
					<text class="detail-card-title">AI 分割结果</text>
					<view class="image-grid" v-if="tumorPicList.length > 0">
						<view
							class="image-cell"
							v-for="(image, index) in tumorPicList"
							:key="'a' + index"
							@click="previewImage(image)"
						>
							<image :src="image" class="cell-img" mode="aspectFill"></image>
						</view>
					</view>
					<view class="ai-empty" v-else>
						<text class="ai-empty-title">暂无 AI 分割结果</text>
						<text class="ai-empty-desc">{{ canRegenerateAi ? '已检测到原始影像，可重新生成 AI 分割图。' : '上传 MRI 影像并完成 AI 分析后，这里会显示分割图。' }}</text>
						<view
							v-if="canRegenerateAi"
							class="ai-gen-btn"
							:class="{ disabled: regeneratingAi }"
							@click="regenerateAiForCurrentRecord"
						>
							<view class="ai-gen-spinner" v-if="regeneratingAi"></view>
							<text class="ai-gen-text">{{ regeneratingAi ? '生成中...' : '生成 AI 分割图' }}</text>
						</view>
					</view>
				</view>

				<!-- 医师签名 -->
				<view class="detail-card sig-card">
					<view class="sig-item">
						<text class="sig-label">报告医师</text>
						<text class="sig-name">{{ doctor[0] }}</text>
					</view>
					<view class="sig-divider"></view>
					<view class="sig-item">
						<text class="sig-label">审核医师</text>
						<text class="sig-name">{{ doctor[1] }}</text>
					</view>
				</view>

				<!-- 操作按钮 -->
				<view class="detail-actions">
					<view class="detail-btn detail-btn-primary" @click="previewReport">
						<text class="detail-btn-text">报告预览</text>
					</view>
					<view class="detail-btn detail-btn-secondary" @click="shareReport">
						<text class="detail-btn-text">分享报告</text>
					</view>
				</view>
			</block>

			<view style="height: 120px;"></view>
		</scroll-view>

		<!-- ===== 添加病历弹窗 ===== -->
		<view class="modal-mask" v-if="showAddForm" @tap="closeAddForm">
			<view class="modal-panel" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">添加病历记录</text>
					<view class="modal-close" @tap="closeAddForm">
						<text class="close-x">✕</text>
					</view>
				</view>

				<scroll-view scroll-y class="modal-body">
					<view class="form-group">
						<text class="form-group-title">基本信息</text>

						<view class="form-field">
							<text class="form-label">就诊日期 <text class="required">*</text></text>
							<textarea class="form-input" v-model="newRecord.visit_date" placeholder="例：2024-10-28 14:30" :auto-height="true" :maxlength="50"></textarea>
						</view>

						<view class="form-field">
							<text class="form-label">科室 <text class="required">*</text></text>
							<view class="form-select" @click="showDepartmentPicker">
								<text class="select-text" :class="{ placeholder: !newRecord.department }">{{ newRecord.department || '请选择科室' }}</text>
								<view class="select-arrow"></view>
							</view>
						</view>

						<view class="form-field">
							<text class="form-label">床号</text>
							<textarea class="form-input" v-model="newRecord.bed_num" placeholder="请输入床号" :auto-height="true" :maxlength="20"></textarea>
						</view>

						<view class="form-field">
							<text class="form-label">检查项目 <text class="required">*</text></text>
							<view class="form-select" @click="showCheckProjectPicker">
								<text class="select-text" :class="{ placeholder: !newRecord.check_project }">{{ newRecord.check_project || '请选择检查项目' }}</text>
								<view class="select-arrow"></view>
							</view>
						</view>

						<view class="form-field">
							<text class="form-label">检查部位</text>
							<view class="form-select" @click="showPositionPicker">
								<text class="select-text" :class="{ placeholder: !newRecord.position }">{{ newRecord.position || '请选择检查部位' }}</text>
								<view class="select-arrow"></view>
							</view>
						</view>
					</view>

					<view class="form-group">
						<text class="form-group-title">检查结果</text>

						<view class="form-field">
							<text class="form-label">影像所见</text>
							<textarea class="form-textarea" v-model="newRecord.imaging_result" placeholder="请输入影像检查所见..." maxlength="500"></textarea>
						</view>

						<view class="form-field">
							<text class="form-label">诊断意见</text>
							<textarea class="form-textarea" v-model="newRecord.diagnosis" placeholder="请输入诊断意见..." maxlength="500"></textarea>
						</view>
					</view>

					<view class="form-group">
						<text class="form-group-title">医学影像（可选）</text>

						<view class="form-field">
							<text class="form-label">上传影像</text>
							<view class="upload-row">
								<view class="upload-pick-btn" @click="chooseImage">
									<text class="upload-pick-text">选择图片</text>
								</view>
								<text class="upload-hint">{{ uploadedImages.length > 0 ? `已选择 ${uploadedImages.length} 张` : '未选择图片' }}</text>
							</view>
						</view>

						<view class="upload-preview" v-if="uploadedImages.length > 0">
							<view class="preview-item" v-for="(img, index) in uploadedImages" :key="index">
								<image :src="img" class="preview-img" mode="aspectFill"></image>
								<view class="preview-remove" @tap="removeImage(index)">
									<text class="remove-x">✕</text>
								</view>
							</view>
						</view>
					</view>
				</scroll-view>

				<view class="modal-footer">
					<view class="modal-btn modal-cancel" @tap="closeAddForm">
						<text class="modal-btn-text">取消</text>
					</view>
					<view class="modal-btn modal-confirm" @tap="submitNewRecord">
						<text class="modal-btn-text">保存</text>
					</view>
				</view>
			</view>
		</view>

		<!-- ===== 选择器弹窗 ===== -->
		<view class="selector-mask" v-if="showSelectorPopup" @tap="closeSelectorPopup">
			<view class="selector-panel" @tap.stop>
				<view class="selector-header">
					<text class="selector-title">{{ selectorTitle }}</text>
					<view class="selector-close" @tap="closeSelectorPopup">
						<text class="close-x">✕</text>
					</view>
				</view>
				<scroll-view scroll-y class="selector-body">
					<view
						class="selector-option"
						v-for="(item, index) in currentSelectorOptions"
						:key="index"
						@tap="selectOption(index)"
					>
						<text class="selector-option-text">{{ item }}</text>
					</view>
				</scroll-view>
			</view>
		</view>

		<bottom-nav-doctor current="patients"></bottom-nav-doctor>
	</view>
</template>

<script>
import BottomNavDoctor from '@/components/bottom_nav/BottomNavDoctor.vue'

export default {
	components: { BottomNavDoctor },
	async onLoad(options) {
		const sys = uni.getSystemInfoSync()
		this.scrollHeight = (sys.windowHeight - 50) + 'px'
		if (options.recordId) {
			await this.loadFromRecordId(options.recordId)
		} else if (options.pat_id) {
			await this.loadFromPatientId(options.pat_id)
		}
	},
	data() {
		return {
			currentRecordId: null,
			currentPatientId: null,
			loading: false,
			scrollHeight: '100vh',
			patient: {
				pat_id: '', check_time: '', name: '', gender: '', age: '',
				host_id: '', department: '', bed_num: '', report_time: '',
				check_project: '', position: '',
			},
			imaging_finding_result: '',
			imaging_diagnosis_result: '',
			doctor: ['', ''],
			primeTumorPicList: [],
			tumorPicList: [],
			canRegenerateAi: false,
			missingAiCount: 0,
			regeneratingAi: false,
			autoRegenerateTried: false,
			medicalRecords: [],
			patientFamilies: [],
			familiesLoaded: false,
			showRecordsList: true,
			showAddForm: false,
			newRecord: {
				visit_date: '', department: '', bed_num: '',
				check_project: '', position: '', imaging_result: '', diagnosis: ''
			},
			uploadedImages: [],
			departmentOptions: ['神经内科', '神经外科', '肿瘤科', '放射科', '影像科', '急诊科', '内科', '外科', '其他'],
			checkProjectOptions: ['头颅MRI平扫', '头颅MRI增强', '头颅CT平扫', '头颅CT增强', '脑部MRI多序列扫描', '颅脑血管造影', '全脑灌注成像', '其他'],
			positionOptions: ['全脑', '额叶', '颞叶', '顶叶', '枕叶', '脑干', '小脑', '基底节区', '其他'],
			showSelectorPopup: false,
			selectorTitle: '',
			currentSelectorOptions: [],
			currentSelectorType: ''
		}
	},
	methods: {
		async loadPatientFamilies(patientId) {
			if (!patientId) return
			try {
				const { djangoRequest } = await import('@/utils/request.js')
				const r = await djangoRequest(`/families/by_patient/?patient_id=${patientId}`)
				console.log('[loadPatientFamilies] patientId:', patientId, 'response:', JSON.stringify(r))
				const bindings = Array.isArray(r) ? r : (r.results || r.bindings || [])
				this.patientFamilies = bindings.filter(b => b.family_user_id).map(b => ({
					family_user_id: b.family_user_id,
					family_name: b.family_name || '家属',
					relationship: b.relationship || ''
				}))
				console.log('[loadPatientFamilies] parsed:', JSON.stringify(this.patientFamilies))
			} catch (e) {
				console.error('[loadPatientFamilies] error:', e)
				this.patientFamilies = []
			} finally {
				this.familiesLoaded = true
			}
		},
		toChatFamily(f) {
			const fid = f.family_user_id || ''
			if (!fid) { uni.showToast({ title: '家属信息不完整', icon: 'none' }); return }
			uni.navigateTo({ url: `/pages/chat/chatDialog?partner_id=${fid}&partner_role=family&partner_name=${encodeURIComponent(f.family_name || '')}` })
		},
		goToFamilyBind() {
			uni.showToast({ title: '请让患者在个人中心生成邀请码，家属扫码绑定', icon: 'none', duration: 3000 })
		},
		async loadFromPatientId(patId) {
			try {
				this.loading = true
				const { patientAPI, medicalRecordAPI } = await import('@/utils/request.js')

				let patientInfo = null
				try {
					const patients = await patientAPI.getPatients()
					const patientsList = Array.isArray(patients) ? patients : (patients.results || [])
					patientInfo = patientsList.find(p => {
						return (p.id?.toString() === patId.toString()) ||
						       (p.id_card === patId) ||
						       (p.pat_id?.toString() === patId.toString()) ||
						       (p._raw?.id?.toString() === patId.toString())
					})
				} catch (e) {
					console.error('获取患者信息失败:', e)
				}

				let isPatient1 = false
				if (patientInfo) {
					const patientUser = patientInfo.user || {}
					const patientUsername = patientUser.username || patientInfo.name || ''
					if (patientUsername === 'patient1' ||
					    patientInfo.id_card === '110101198506150011' ||
					    (patientInfo.name === '王先生' && patientInfo.id_card?.includes('110101'))) {
						isPatient1 = true
						this.loadPatient1MockData()
					}
				}

				if (!patientInfo) {
					uni.showToast({ title: '未找到该患者', icon: 'none' })
					this.loading = false
					return
				}

				this.currentPatientId = patientInfo.id || patientInfo._raw?.id
				this.patient = {
					pat_id: patientInfo.id_card || patientInfo.id || '',
					name: patientInfo.name || '',
					gender: patientInfo.gender === 'M' ? '男' : '女',
					age: patientInfo.age || '',
					host_id: patientInfo.id?.toString() || '',
				}
				this.loadPatientFamilies(this.currentPatientId)

				const response = await medicalRecordAPI.getRecords()
				let records = Array.isArray(response) ? response : (response.results || [])
				const patientId = patientInfo.id || patientInfo._raw?.id
				const patientRecords = records.filter(r => {
					const rId = r.patient?.id || r.patient_id
					return rId?.toString() === patientId?.toString()
				})

				if (patientRecords.length > 0) {
					patientRecords.sort((a, b) => new Date(b.visit_date || b.created_at || 0) - new Date(a.visit_date || a.created_at || 0))

					const envConfigModule = await import('@/config/env.config.js')
					const ENV_CONFIG = envConfigModule.default || envConfigModule
					const baseUrl = ENV_CONFIG.DJANGO_BASE_URL.replace('/api', '')

					const realRecords = patientRecords.map(record => {
						const ctScan = record.ct_scans && record.ct_scans.length > 0 ? record.ct_scans[0] : null
						let checkTime = record.visit_date || record.created_at
						if (checkTime) {
							const d = new Date(checkTime)
							checkTime = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
						}
						let imgUrl = ''
						if (ctScan?.processed_image) {
							imgUrl = ctScan.processed_image.startsWith('http') ? ctScan.processed_image : ctScan.processed_image.startsWith('/media/') ? `${baseUrl}${ctScan.processed_image}` : `${baseUrl}/media/${ctScan.processed_image}`
						} else if (ctScan?.original_image) {
							imgUrl = ctScan.original_image.startsWith('http') ? ctScan.original_image : ctScan.original_image.startsWith('/media/') ? `${baseUrl}${ctScan.original_image}` : `${baseUrl}/media/${ctScan.original_image}`
						}
						return {
							id: record.id,
							check_time: checkTime,
							department: record.department || record.doctor?.department || '未知科室',
							check_project: record.check_project || (ctScan ? `CT扫描 (${this.getScanModeText(ctScan.scan_mode)})` : '医疗检查'),
							img_url: imgUrl,
							imaging_finding_result: record.notes || ctScan?.ai_analysis || ctScan?.doctor_review || record.diagnosis || '暂无检查结果',
							diagnosis_opinion: record.diagnosis || record.notes || '暂无诊断意见',
							raw_data: record,
							is_demo: false
						}
					})

					if (isPatient1) {
						this.medicalRecords = [...this.medicalRecords, ...realRecords]
					} else {
						this.medicalRecords = realRecords
					}
				} else {
					if (!isPatient1) {
						this.medicalRecords = []
						uni.showToast({ title: '该患者暂无医疗记录', icon: 'none', duration: 2000 })
					}
				}
			} catch (error) {
				console.error('加载患者病历失败:', error)
				uni.showToast({ title: '加载失败', icon: 'none' })
			} finally {
				this.loading = false
			}
		},

		loadPatient1MockData() {
			this.currentPatientId = 1
			this.patient = {
				pat_id: '110101198506150011', name: '王先生', gender: '男',
				age: 40, host_id: '1',
			}
			this.medicalRecords = [
				{
					id: 'demo-1', check_time: '2024-10-11 10:02', department: '神经重症医学科(NICU)',
					check_project: '头颅MRI平扫', img_url: '/static/tumorPic/1.jpg',
					imaging_finding_result: '右侧颞叶可见异常信号影，大小约3.2×2.8cm，边界欠清晰，周围可见水肿带。建议进一步检查确诊。',
					diagnosis_opinion: '右侧颞叶占位性病变，考虑：1.胶质瘤可能性大 2.建议增强MRI进一步检查',
					is_demo: true,
					full_data: {
						pat_id: '110101198506150011', check_time: '2024-10-11 10:02',
						name: '王先生', gender: '男', age: 40, host_id: '1',
						department: '神经重症医学科(NICU)', bed_num: 18,
						report_time: '2024-10-11 10:02', check_project: '头颅MRI平扫', position: '105层',
						imaging_finding_result: '右侧颞叶可见异常信号影，大小约3.2×2.8cm，边界欠清晰，周围可见水肿带。建议进一步检查确诊。',
						imaging_diagnosis_result: '右侧颞叶占位性病变，考虑：1.胶质瘤可能性大 2.建议增强MRI进一步检查',
						doctor: ['张医生', '李医生'],
						primeTumorPicList: ['/static/tumorPic/1.jpg'],
						tumorPicList: ['/static/tumorPic/2.jpg']
					}
				},
				{
					id: 'demo-2', check_time: '2024-09-28 14:30', department: '神经外科',
					check_project: '头颅MRI增强', img_url: '/static/tumorPic/2.jpg',
					imaging_finding_result: '增强扫描显示病灶明显强化，呈环形强化特征，中心坏死区未见强化。',
					diagnosis_opinion: '结合平扫及增强表现，高度怀疑高级别胶质瘤，建议手术治疗。',
					is_demo: true,
					full_data: {
						pat_id: '110101198506150011', check_time: '2024-09-28 14:30',
						name: '王先生', gender: '男', age: 40, host_id: '1',
						department: '神经外科', bed_num: 12,
						report_time: '2024-09-28 15:00', check_project: '头颅MRI增强', position: '120层',
						imaging_finding_result: '增强扫描显示病灶明显强化，呈环形强化特征，中心坏死区未见强化。',
						imaging_diagnosis_result: '结合平扫及增强表现，高度怀疑高级别胶质瘤，建议手术治疗。',
						doctor: ['张医生', '李医生'],
						primeTumorPicList: ['/static/tumorPic/2.jpg'],
						tumorPicList: ['/static/tumorPic/1.jpg', '/static/tumorPic/3.jpg']
					}
				}
			]
			this.showRecordsList = true
			this.loading = false
		},

		async loadFromRecordId(recordId) {
			try {
				this.loading = true
				if (this.currentRecordId !== recordId) this.autoRegenerateTried = false
				const { medicalRecordAPI } = await import('@/utils/request.js')
				const record = await medicalRecordAPI.getRecord(recordId)
				this.currentRecordId = recordId
				await this.processMedicalRecord(record)
				this.showRecordsList = false
			} catch (error) {
				console.error('加载病历详情失败:', error)
				uni.showToast({ title: '加载详情失败', icon: 'none' })
			} finally {
				this.loading = false
			}
		},

		async viewRecordDetail(record) {
			if (record.is_demo && record.full_data) {
				this.currentRecordId = record.id
				const d = record.full_data
				this.patient = {
					pat_id: d.pat_id, check_time: d.check_time, name: d.name,
					gender: d.gender, age: d.age, host_id: d.host_id,
					department: d.department, bed_num: d.bed_num,
					report_time: d.report_time, check_project: d.check_project, position: d.position,
				}
				this.imaging_finding_result = d.imaging_finding_result
				this.imaging_diagnosis_result = d.imaging_diagnosis_result
				this.doctor = d.doctor
				this.primeTumorPicList = d.primeTumorPicList
				this.tumorPicList = d.tumorPicList
				this.showRecordsList = false
			} else if (record.id) {
				await this.loadFromRecordId(record.id)
			}
		},

		backToList() {
			this.showRecordsList = true
		},

		showAddRecordForm() {
			this.newRecord = {
				visit_date: this.formatCurrentDate(), department: '', bed_num: '',
				check_project: '', position: '', imaging_result: '', diagnosis: ''
			}
			this.uploadedImages = []
			this.showAddForm = true
		},
		showDepartmentPicker() {
			this.selectorTitle = '选择科室'
			this.currentSelectorOptions = this.departmentOptions
			this.currentSelectorType = 'department'
			this.showSelectorPopup = true
		},
		showCheckProjectPicker() {
			this.selectorTitle = '选择检查项目'
			this.currentSelectorOptions = this.checkProjectOptions
			this.currentSelectorType = 'checkProject'
			this.showSelectorPopup = true
		},
		showPositionPicker() {
			this.selectorTitle = '选择检查部位'
			this.currentSelectorOptions = this.positionOptions
			this.currentSelectorType = 'position'
			this.showSelectorPopup = true
		},
		selectOption(index) {
			const val = this.currentSelectorOptions[index]
			if (this.currentSelectorType === 'department') this.newRecord.department = val
			else if (this.currentSelectorType === 'checkProject') this.newRecord.check_project = val
			else if (this.currentSelectorType === 'position') this.newRecord.position = val
			this.closeSelectorPopup()
		},
		closeSelectorPopup() { this.showSelectorPopup = false },
		closeAddForm() {
			this.showAddForm = false
			this.newRecord = { visit_date: '', department: '', bed_num: '', check_project: '', position: '', imaging_result: '', diagnosis: '' }
			this.uploadedImages = []
		},
		formatCurrentDate() {
			const n = new Date()
			return `${n.getFullYear()}-${String(n.getMonth()+1).padStart(2,'0')}-${String(n.getDate()).padStart(2,'0')} ${String(n.getHours()).padStart(2,'0')}:${String(n.getMinutes()).padStart(2,'0')}`
		},
		chooseImage() {
			uni.chooseImage({
				count: 5, sizeType: ['compressed'], sourceType: ['album', 'camera'],
				success: (res) => { this.uploadedImages = [...this.uploadedImages, ...res.tempFilePaths] },
				fail: () => { uni.showToast({ title: '选择图片失败', icon: 'none' }) }
			})
		},
		removeImage(index) { this.uploadedImages.splice(index, 1) },

		async submitNewRecord() {
			if (!this.newRecord.visit_date || !this.newRecord.department || !this.newRecord.check_project) {
				uni.showToast({ title: '请填写必填项', icon: 'none', duration: 2000 })
				return
			}
			if (!this.currentPatientId) {
				uni.showToast({ title: '缺少患者信息', icon: 'none' })
				return
			}
			try {
				uni.showLoading({ title: '保存中...', mask: true })
				const { medicalRecordAPI } = await import('@/utils/request.js')
				const recordData = {
					patient_id: this.currentPatientId,
					visit_date: this.newRecord.visit_date,
					department: this.newRecord.department || '',
					bed_num: this.newRecord.bed_num || '',
					check_project: this.newRecord.check_project || '',
					position: this.newRecord.position || '',
					diagnosis: this.newRecord.diagnosis || '',
					notes: this.newRecord.imaging_result || '',
					status: 'completed'
				}
				const createdRecord = await medicalRecordAPI.createRecord(recordData)

				if (this.uploadedImages.length > 0) {
					for (let i = 0; i < this.uploadedImages.length; i++) {
						try {
							const envConfigModule = require('@/config/env.config.js')
							const ENV_CONFIG = envConfigModule.default || envConfigModule
							const token = uni.getStorageSync('token')
							await new Promise((resolve, reject) => {
								uni.uploadFile({
									url: `${ENV_CONFIG.DJANGO_BASE_URL}/medical-records/${createdRecord.id}/upload_ct_scan/`,
									filePath: this.uploadedImages[i],
									name: 'original_image',
									formData: { 'scan_mode': 't1' },
									header: { 'Authorization': `Token ${token}` },
									success: (res) => res.statusCode === 200 ? resolve(res) : reject(new Error(`上传失败: ${res.statusCode}`)),
									fail: reject
								})
							})
						} catch (e) { /* 继续 */ }
					}
				}
				uni.hideLoading()
				uni.showToast({ title: '保存成功', icon: 'success', duration: 2000 })
				this.closeAddForm()
				await this.loadFromPatientId(this.currentPatientId)
			} catch (error) {
				uni.hideLoading()
				let errorMsg = '保存失败'
				if (error.response?.data) {
					const d = error.response.data
					errorMsg = typeof d === 'string' ? d : d.error || d.detail || JSON.stringify(d)
				} else if (error.message) {
					errorMsg = error.message
				}
				uni.showToast({ title: errorMsg, icon: 'none', duration: 5000 })
			}
		},

		async processMedicalRecord(record) {
			let ctScans = record.ct_scans && record.ct_scans.length > 0 ? record.ct_scans : []
			const formatDate = (s) => {
				if (!s) return ''
				const d = new Date(s)
				return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
			}
			const envConfigModule = await import('@/config/env.config.js')
			const ENV_CONFIG = envConfigModule.default || envConfigModule
			const baseUrl = ENV_CONFIG.DJANGO_BASE_URL.replace('/api', '')

			this.primeTumorPicList = []
			this.tumorPicList = []
			let missingAiCount = 0

			ctScans.forEach(ct => {
				if (ct.original_image) this.primeTumorPicList.push(this.formatMediaUrl(ct.original_image, baseUrl))
				if (ct.processed_image) {
					this.tumorPicList.push(this.formatMediaUrl(ct.processed_image, baseUrl))
				} else if (ct.original_image) {
					missingAiCount++
				}
			})
			this.canRegenerateAi = missingAiCount > 0
			this.missingAiCount = missingAiCount

			const first = ctScans.length > 0 ? ctScans[0] : null
			this.patient = {
				pat_id: record.patient?.id_card || record.patient?.id || '',
				check_time: formatDate(record.visit_date || record.created_at),
				name: record.patient?.name || '',
				gender: record.patient?.gender === 'M' ? '男' : '女',
				age: record.patient?.age || '',
				host_id: record.patient?.id?.toString() || '',
				department: record.department || record.doctor?.department || '未知科室',
				bed_num: record.bed_num || record.patient?.bed_num || '',
				report_time: formatDate(record.updated_at || record.created_at),
				check_project: record.check_project || (first ? `CT扫描 (${this.getScanModeText(first.scan_mode)})` : '医疗检查'),
				position: record.position || first?.tumor_location || '',
			}
			this.imaging_finding_result = record.notes || first?.ai_analysis || first?.doctor_review || record.diagnosis || '暂无检查结果'
			this.imaging_diagnosis_result = record.diagnosis || '暂无诊断意见'
			const dName = record.doctor?.name || '待填写'
			this.doctor = [dName, dName]
			if (record.patient) { this.currentPatientId = record.patient.id; this.loadPatientFamilies(record.patient.id) }

			if (this.tumorPicList.length === 0 && missingAiCount > 0 && !this.autoRegenerateTried) {
				this.autoRegenerateTried = true
				await this.regenerateAiForCurrentRecord(true)
			}
		},

		formatMediaUrl(path, baseUrl) {
			if (!path) return ''
			if (path.startsWith('http')) return path
			if (path.startsWith('/media/')) return `${baseUrl}${path}`
			return `${baseUrl}/media/${path}`
		},

		async regenerateAiForCurrentRecord(silent = false) {
			if (!this.currentRecordId || this.regeneratingAi) return
			this.regeneratingAi = true
			try {
				uni.showLoading({ title: '生成AI分割图...', mask: true })
				const { medicalRecordAPI } = await import('@/utils/request.js')
				const resp = await medicalRecordAPI.reanalyzeCTScans(this.currentRecordId)
				uni.hideLoading()
				if (resp.processed_count > 0) {
					if (!silent) uni.showToast({ title: 'AI分割图已生成', icon: 'success' })
					await this.loadFromRecordId(this.currentRecordId)
					return
				}
				uni.showToast({ title: resp.message || '没有可生成的影像', icon: 'none', duration: 2500 })
			} catch (error) {
				uni.hideLoading()
				uni.showToast({ title: error.response?.data?.error || error.message || 'AI生成失败', icon: 'none', duration: 3000 })
			} finally {
				this.regeneratingAi = false
			}
		},

		toManagePage() { uni.navigateBack() },

		previewReport() {
			if (this.currentRecordId) {
				uni.navigateTo({ url: `/pages/previewReport/previewReport?recordId=${this.currentRecordId}` })
			} else if (this.patient.pat_id) {
				uni.navigateTo({ url: `/pages/previewReport/previewReport?pat_id=${this.patient.pat_id}` })
			} else {
				uni.showToast({ title: '无法预览报告', icon: 'none' })
			}
		},

		shareReport() {
			uni.showActionSheet({
				itemList: ['发送给患者', '打印报告'],
				success: async (res) => {
					if (res.tapIndex === 0) await this.sendToPatient()
					else if (res.tapIndex === 1) this.printReport()
				}
			})
		},

		async sendToPatient() {
			if (!this.currentRecordId || !this.currentPatientId) {
				uni.showToast({ title: '缺少必要信息', icon: 'none' })
				return
			}
			try {
				uni.showLoading({ title: '发送中...', mask: true })
				const { notificationAPI } = await import('@/utils/request.js')
				await notificationAPI.sendToPatient({
					patient_id: this.currentPatientId,
					medical_record_id: this.currentRecordId,
					title: `检查报告通知 - ${this.patient.check_project || '医疗检查'}`,
					content: `您的${this.patient.check_project || '医疗检查'}报告已生成，请及时查看。检查时间：${this.patient.check_time}`
				})
				uni.hideLoading()
				uni.showToast({ title: '已发送给患者', icon: 'success', duration: 2000 })
			} catch (error) {
				uni.hideLoading()
				uni.showToast({ title: error.message || '发送失败', icon: 'none', duration: 3000 })
			}
		},

		printReport() {
			// #ifdef H5
			window.print()
			// #endif
			// #ifndef H5
			uni.showModal({
				title: '打印提示', content: '请使用报告预览功能，然后通过浏览器打印功能进行打印。',
				showCancel: false,
				success: () => { this.previewReport() }
			})
			// #endif
		},

		getScanModeText(m) {
			return { '1': '平扫', '2': '增强', t1: 'T1', t2: 'T2', t1ce: 'T1CE', flair: 'FLAIR' }[m] || m || '其他'
		},

		previewImage(image) {
			const all = [...this.primeTumorPicList, ...this.tumorPicList]
			if (all.length === 0) {
				uni.showToast({ title: '暂无可预览图像', icon: 'none' })
				return
			}
			uni.previewImage({ urls: all, current: image })
		}
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); position: relative; overflow: hidden; overflow-x: hidden; width: 100%; box-sizing: border-box; }
.scroll-area { position: relative; z-index: 1; overflow-x: hidden; max-width: 100%; box-sizing: border-box; }

/* 导航栏 */
.navbar {
	position: relative; z-index: 10;
	padding: 48px 16px 14px;
	background: rgba(244,246,251,0.85);
	backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px);
	border-bottom: 1px solid var(--ds-hairline);
}
.navbar-inner { display: flex; align-items: center; min-width: 0; }
.navbar-left { width: 36px; height: 36px; border-radius: 10px; background: var(--ds-bg-sunken); display: flex; align-items: center; justify-content: center; }
.navbar-left:active { background: var(--ds-brand-ghost); }
.back-arrow { width: 10px; height: 10px; border-left: 2px solid var(--ds-ink-3); border-bottom: 2px solid var(--ds-ink-3); transform: rotate(45deg); margin-left: 3px; }
.navbar-center { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 2px; }
.navbar-title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); }
.navbar-sub { font-size: 11px; color: var(--ds-ink-4); }
.navbar-right { width: 36px; }

/* 家属联系 */
.family-contact-section { margin: 16px 20px 0; }
.family-contact-card { background: var(--ds-surface); border-radius: 14px; border: 1px solid var(--ds-hairline); padding: 14px 16px; box-shadow: var(--ds-shadow-sm); overflow: hidden; }
.family-contact-title { display: block; font-size: 12px; font-weight: 700; color: var(--ds-ink-4); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; }
.family-contact-title.has-family-title { color: var(--ds-success); }
.family-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; }
.family-item + .family-item { border-top: 1px solid var(--ds-hairline); }
.family-avatar-sm { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #F5A623 0%, #FF7A59 100%); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.family-avatar-sm-text { font-size: 14px; font-weight: 700; color: #fff; }
.family-info { flex: 1; min-width: 0; }
.family-name { display: block; font-size: 14px; font-weight: 600; color: var(--ds-ink-1); }
.family-rel { display: block; font-size: 12px; color: var(--ds-ink-3); margin-top: 2px; }
.family-msg-btn { display: flex; align-items: center; gap: 4px; padding: 6px 12px; border-radius: 20px; background: var(--ds-brand-soft); flex-shrink: 0; }
.family-msg-pressed { background: rgba(10,92,255,0.18); }
.family-msg-icon { font-size: 13px; color: var(--ds-brand); }
.family-msg-text { font-size: 12px; font-weight: 600; color: var(--ds-brand); }
.family-empty-card { background: rgba(31,184,119,0.08); border-radius: 14px; border: 1px solid rgba(31,184,119,0.2); padding: 16px; display: flex; align-items: center; gap: 10px; transition: background 0.18s; }
.family-empty-pressed { background: rgba(31,184,119,0.14); }
.family-empty-icon { font-size: 20px; flex-shrink: 0; }
.family-empty-text { font-size: 14px; font-weight: 600; color: var(--ds-success); }
.family-empty-sub { font-size: 11px; color: var(--ds-ink-4); margin-left: auto; }

/* 患者卡片 */
.patient-card {
	margin: 20px;
	background: var(--ds-surface);
	border: 1px solid var(--ds-hairline);
	border-radius: 20px;
	padding: 20px;
	display: flex; gap: 16px;
	box-shadow: var(--ds-shadow-sm);
	animation: fadeSlideUp 0.4s ease both;
	overflow: hidden;
}
.patient-avatar { flex-shrink: 0; }
.avatar-img { width: 64px; height: 64px; border-radius: 16px; border: 2px solid var(--ds-hairline); }
.patient-info { flex: 1; min-width: 0; }
.patient-name { display: block; font-size: 22px; font-weight: 700; color: var(--ds-ink-1); margin-bottom: 10px; }
.patient-meta { display: flex; gap: 12px; flex-wrap: wrap; }
.meta-tag { display: flex; flex-direction: column; gap: 2px; }
.meta-label { font-size: 10px; color: var(--ds-ink-4); text-transform: uppercase; letter-spacing: 0.5px; }
.meta-value { font-size: 14px; font-weight: 500; color: var(--ds-ink-2); }

/* 记录列表 */
.records-section { padding: 0 20px; overflow: hidden; }
.records-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.records-title { font-size: 16px; font-weight: 600; color: var(--ds-ink-1); }
.records-actions { display: flex; align-items: center; gap: 10px; }
.records-count { font-size: 12px; color: var(--ds-ink-4); }
.add-btn { padding: 6px 14px; border-radius: 20px; background: rgba(31,184,119,0.1); border: 1px solid rgba(31,184,119,0.2); }
.add-btn:active { background: rgba(31,184,119,0.18); }
.add-btn-text { font-size: 12px; font-weight: 600; color: var(--ds-success); }

/* 加载/空状态 */
.loading-state { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; gap: 14px; }
.loading-spinner { width: 32px; height: 32px; border: 2px solid var(--ds-hairline); border-top-color: var(--ds-cyan); border-radius: 50%; animation: spin 0.8s linear infinite; }
.loading-text { font-size: 13px; color: var(--ds-ink-3); }

.empty-state { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; gap: 12px; }
.empty-icon-wrap { width: 56px; height: 56px; border-radius: 50%; background: var(--ds-bg-sunken); border: 1px solid var(--ds-hairline); display: flex; align-items: center; justify-content: center; }
.empty-icon-text { font-size: 24px; font-weight: 700; color: var(--ds-ink-4); }
.empty-title { font-size: 16px; font-weight: 600; color: var(--ds-ink-2); }
.empty-desc { font-size: 13px; color: var(--ds-ink-4); }

/* 记录卡片 */
.record-card {
	background: var(--ds-surface);
	border: 1px solid var(--ds-hairline);
	border-radius: 16px;
	padding: 16px;
	margin-bottom: 12px;
	box-shadow: var(--ds-shadow-sm);
	animation: fadeSlideUp 0.4s ease both;
	transition: all 0.25s;
	overflow: hidden;
}
.record-card:active { transform: scale(0.985); border-color: rgba(0,194,215,0.25); }

.record-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid var(--ds-hairline); min-width: 0; gap: 8px; }
.record-date-wrap { display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1; overflow: hidden; }
.record-date { font-size: 13px; color: var(--ds-ink-4); }
.real-badge { padding: 2px 8px; border-radius: 10px; background: var(--ds-brand-soft); }
.real-badge-text { font-size: 10px; font-weight: 600; color: var(--ds-brand); }

.record-status-tag { display: flex; align-items: center; gap: 5px; flex-shrink: 0; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--ds-cyan); }
.status-text { font-size: 11px; color: var(--ds-cyan); font-weight: 500; }

.record-body { display: flex; gap: 12px; align-items: center; min-width: 0; overflow: hidden; }
.record-thumb { width: 64px; height: 64px; border-radius: 12px; overflow: hidden; flex-shrink: 0; background: var(--ds-bg-sunken); }
.thumb-img { width: 100%; height: 100%; }
.record-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; overflow: hidden; }
.record-project { font-size: 14px; font-weight: 600; color: var(--ds-ink-1); }
.record-result { font-size: 12px; color: var(--ds-ink-3); line-height: 1.4; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; line-clamp: 2; overflow: hidden; }
.record-dept { font-size: 11px; color: var(--ds-brand); }
.record-arrow { flex-shrink: 0; width: 28px; height: 28px; border-radius: 50%; background: var(--ds-bg-sunken); display: flex; align-items: center; justify-content: center; }
.arrow-icon { width: 6px; height: 6px; border-right: 1.5px solid var(--ds-ink-4); border-bottom: 1.5px solid var(--ds-ink-4); transform: rotate(-45deg); margin-left: -2px; }

/* 详情视图 */
.back-row { padding: 16px 20px 0; }
.back-pill { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 20px; background: var(--ds-bg-sunken); border: 1px solid var(--ds-hairline); }
.back-pill:active { background: var(--ds-brand-ghost); }
.back-arrow-sm { width: 8px; height: 8px; border-left: 1.5px solid var(--ds-ink-3); border-bottom: 1.5px solid var(--ds-ink-3); transform: rotate(45deg); margin-left: 2px; }
.back-pill-text { font-size: 13px; color: var(--ds-ink-2); }

.detail-card {
	margin: 16px 20px;
	background: var(--ds-surface);
	border: 1px solid var(--ds-hairline);
	border-radius: 16px;
	padding: 18px;
	box-shadow: var(--ds-shadow-sm);
	overflow: hidden;
}
.detail-card-title { display: block; font-size: 13px; font-weight: 600; color: var(--ds-ink-4); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px; }

.info-grid { display: flex; gap: 14px; margin-bottom: 12px; overflow: hidden; }
.info-grid-3 { gap: 10px; }
.info-cell { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.info-key { font-size: 10px; color: var(--ds-ink-4); text-transform: uppercase; letter-spacing: 0.5px; }
.info-val { font-size: 14px; font-weight: 500; color: var(--ds-ink-1); }
.info-row-single { display: flex; flex-direction: column; gap: 3px; margin-bottom: 12px; }
.info-divider { height: 1px; background: var(--ds-hairline); margin: 14px 0; }

.detail-text { font-size: 14px; color: var(--ds-ink-2); line-height: 1.8; }

/* 诊断卡片 */
.diagnosis-card { display: flex; gap: 14px; background: rgba(255,107,107,0.04); border-color: rgba(255,107,107,0.12); }
.diagnosis-bar { width: 3px; border-radius: 2px; background: linear-gradient(180deg, #FF6B6B, #FF4757); flex-shrink: 0; }
.diagnosis-inner { flex: 1; }
.diagnosis-title { display: block; font-size: 13px; font-weight: 600; color: #FF6B6B; margin-bottom: 8px; }
.diagnosis-text { font-size: 14px; color: var(--ds-ink-2); line-height: 1.8; }

/* 图像网格 */
.image-grid { display: flex; flex-wrap: wrap; gap: 10px; overflow: hidden; }
.image-cell { width: calc(50% - 5px); aspect-ratio: 1; border-radius: 12px; overflow: hidden; background: var(--ds-bg-sunken); border: 1px solid var(--ds-hairline); box-sizing: border-box; }
.cell-img { width: 100%; height: 100%; }

/* AI 空状态 */
.ai-empty { padding: 24px 16px; text-align: center; border: 1px dashed var(--ds-hairline); border-radius: 12px; background: var(--ds-bg-sunken); }
.ai-empty-title { display: block; font-size: 15px; font-weight: 600; color: var(--ds-ink-2); margin-bottom: 8px; }
.ai-empty-desc { display: block; font-size: 13px; color: var(--ds-ink-3); line-height: 1.6; }
.ai-gen-btn { margin: 16px auto 0; display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; border-radius: 12px; background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); }
.ai-gen-btn.disabled { opacity: 0.5; pointer-events: none; }
.ai-gen-btn:active { transform: scale(0.97); }
.ai-gen-spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; }
.ai-gen-text { font-size: 13px; font-weight: 600; color: #fff; }

/* 签名 */
.sig-card { display: flex; align-items: center; }
.sig-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; }
.sig-label { font-size: 11px; color: var(--ds-ink-4); }
.sig-name { font-size: 15px; font-weight: 600; color: var(--ds-ink-1); }
.sig-divider { width: 1px; height: 28px; background: var(--ds-hairline); margin: 0 16px; }

/* 操作按钮 */
.detail-actions { display: flex; gap: 12px; padding: 16px 20px; overflow: hidden; }
.detail-btn { flex: 1; padding: 16px; border-radius: 14px; display: flex; align-items: center; justify-content: center; transition: all 0.3s; }
.detail-btn:active { transform: scale(0.97); }
.detail-btn-primary { background: var(--ds-grad-brand); }
.detail-btn-secondary { background: var(--ds-bg-sunken); border: 1px solid var(--ds-hairline); }
.detail-btn-text { font-size: 15px; font-weight: 600; color: #fff; }
.detail-btn-secondary .detail-btn-text { color: var(--ds-ink-2); }

/* ===== 弹窗 ===== */
.modal-mask {
	position: fixed; top: 0; left: 0; right: 0; bottom: 0;
	background: rgba(12,23,51,0.45);
	backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
	z-index: 9999;
	display: flex; align-items: center; justify-content: center;
	padding: 16px;
}
.modal-panel {
	background: var(--ds-surface);
	border: 1px solid var(--ds-hairline);
	border-radius: 20px;
	width: 100%;
	max-width: 500px;
	max-height: 88vh;
	display: flex;
	flex-direction: column;
	box-shadow: var(--ds-shadow-lg);
	animation: modalSlideUp 0.3s ease;
	overflow: hidden;
}
.modal-header {
	display: flex; justify-content: space-between; align-items: center;
	padding: 20px;
	border-bottom: 1px solid var(--ds-hairline);
}
.modal-title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); }
.modal-close { width: 32px; height: 32px; border-radius: 50%; background: var(--ds-bg-sunken); display: flex; align-items: center; justify-content: center; }
.close-x { font-size: 16px; color: var(--ds-ink-3); }

.modal-body { flex: 1; overflow-y: auto; overflow-x: hidden; padding: 20px; box-sizing: border-box; max-width: 100%; }
.form-group { margin-bottom: 24px; overflow: hidden; }
.form-group-title { display: block; font-size: 13px; font-weight: 600; color: var(--ds-brand); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid var(--ds-brand-soft); }
.form-field { margin-bottom: 16px; }
.form-label { display: block; font-size: 13px; color: var(--ds-ink-2); margin-bottom: 8px; }
.required { color: var(--ds-danger); margin-left: 2px; }
.form-input {
	width: 100%; min-height: 44px; padding: 12px 14px;
	border: 1px solid var(--ds-hairline);
	border-radius: 10px;
	font-size: 14px;
	color: var(--ds-ink-1);
	background: var(--ds-bg-sunken);
	box-sizing: border-box;
	max-width: 100%;
}
.form-input:focus { border-color: var(--ds-brand); }
.form-textarea {
	width: 100%; min-height: 80px; padding: 12px 14px;
	border: 1px solid var(--ds-hairline);
	border-radius: 10px;
	font-size: 14px;
	color: var(--ds-ink-1);
	background: var(--ds-bg-sunken);
	resize: vertical;
	box-sizing: border-box;
	max-width: 100%;
}
.form-select {
	width: 100%; min-height: 44px; padding: 12px 14px;
	border: 1px solid var(--ds-hairline);
	border-radius: 10px;
	background: var(--ds-bg-sunken);
	display: flex; justify-content: space-between; align-items: center;
	box-sizing: border-box;
	max-width: 100%;
}
.select-text { font-size: 14px; color: var(--ds-ink-1); }
.select-text.placeholder { color: var(--ds-ink-4); }
.select-arrow { width: 8px; height: 8px; border-right: 1.5px solid var(--ds-ink-4); border-bottom: 1.5px solid var(--ds-ink-4); transform: rotate(45deg); }

.upload-row { display: flex; align-items: center; gap: 12px; }
.upload-pick-btn { padding: 8px 16px; border-radius: 10px; background: var(--ds-brand-soft); border: 1px solid rgba(10,92,255,0.2); }
.upload-pick-btn:active { background: rgba(10,92,255,0.15); }
.upload-pick-text { font-size: 13px; font-weight: 600; color: var(--ds-brand); }
.upload-hint { font-size: 13px; color: var(--ds-ink-4); }

.upload-preview { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 12px; }
.preview-item { position: relative; width: 64px; height: 64px; border-radius: 10px; overflow: hidden; border: 1px solid var(--ds-hairline); }
.preview-img { width: 100%; height: 100%; }
.preview-remove { position: absolute; top: 2px; right: 2px; width: 18px; height: 18px; background: rgba(0,0,0,0.5); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.remove-x { font-size: 12px; color: #fff; }

.modal-footer { display: flex; gap: 12px; padding: 16px 20px; border-top: 1px solid var(--ds-hairline); }
.modal-btn { flex: 1; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.modal-btn:active { transform: scale(0.97); }
.modal-cancel { background: var(--ds-bg-sunken); }
.modal-confirm { background: var(--ds-grad-brand); }
.modal-btn-text { font-size: 15px; font-weight: 600; color: #fff; }
.modal-cancel .modal-btn-text { color: var(--ds-ink-2); }

/* 选择器弹窗 */
.selector-mask {
	position: fixed; top: 0; left: 0; right: 0; bottom: 0;
	background: rgba(12,23,51,0.45);
	z-index: 9999;
	display: flex; align-items: flex-end;
}
.selector-panel {
	width: 100%;
	max-height: 60vh;
	background: var(--ds-surface);
	border: 1px solid var(--ds-hairline);
	border-radius: 20px 20px 0 0;
	display: flex; flex-direction: column;
	box-shadow: var(--ds-shadow-lg);
}
.selector-header {
	display: flex; justify-content: space-between; align-items: center;
	padding: 20px;
	border-bottom: 1px solid var(--ds-hairline);
}
.selector-title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); }
.selector-close { width: 32px; height: 32px; border-radius: 50%; background: var(--ds-bg-sunken); display: flex; align-items: center; justify-content: center; }
.selector-body { flex: 1; overflow-y: auto; }
.selector-option { padding: 16px 20px; border-bottom: 1px solid var(--ds-hairline); }
.selector-option:active { background: var(--ds-bg-sunken); }
.selector-option-text { font-size: 15px; color: var(--ds-ink-1); }

/* 动画 */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeSlideUp {
	from { opacity: 0; transform: translateY(16px); }
	to { opacity: 1; transform: translateY(0); }
}
@keyframes modalSlideUp {
	from { opacity: 0; transform: translateY(40px); }
	to { opacity: 1; transform: translateY(0); }
}
</style>
