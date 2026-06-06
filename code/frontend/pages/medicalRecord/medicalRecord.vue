<template>
	<view class="medical-record-page">
		<!-- 自定义导航栏 -->
		<view class="custom-navbar">
			<view class="navbar-content">
				<view class="navbar-center-full">
					<text class="navbar-title">我的病历</text>
					<text class="navbar-subtitle">Medical Records</text>
				</view>
				<view class="navbar-right">
					<text class="menu-icon">⋮</text>
				</view>
			</view>
		</view>
		
		<!-- 患者信息卡片 -->
		<view class="patient-info-card">
			<view class="patient-avatar-wrapper">
				<image :src="patient.gender === '男' ? img_url.boy : img_url.girl" class="patient-avatar" mode="aspectFill"></image>
			</view>
			<view class="patient-details">
				<text class="patient-name">{{ patient.name }}</text>
				<view class="patient-meta">
					<view class="meta-item">
						<text class="meta-label">性别</text>
						<text class="meta-value">{{ patient.gender }}</text>
					</view>
					<view class="meta-item">
						<text class="meta-label">年龄</text>
						<text class="meta-value">{{ patient.age }}岁</text>
					</view>
					<view class="meta-item">
						<text class="meta-label">病历号</text>
						<text class="meta-value">{{ patient.pat_id }}</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 病历记录列表 -->
		<view class="records-container">
			<view class="section-header">
				<text class="section-title">就诊记录</text>
				<view class="header-right">
					<text class="record-count">共{{ patient.medical_record.length }}条</text>
					<button class="add-record-btn" @tap="showAddRecordForm" type="default" size="mini">+ 添加病历</button>
				</view>
			</view>
			
			<!-- 加载状态 -->
			<view class="loading-container" v-if="loading">
				<view class="loading-spinner"></view>
				<text class="loading-text">加载中...</text>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-else-if="patient.medical_record.length === 0">
				<text class="empty-icon">📋</text>
				<text class="empty-title">暂无就诊记录</text>
				<text class="empty-desc">您还没有任何就诊记录</text>
			</view>
			
			<!-- 记录卡片 -->
			<view 
				class="record-card" 
				v-for="(record, index) in patient.medical_record" 
				:key="index"
				@click="toDetailPage(index)"
				:style="{animationDelay: index * 0.1 + 's'}"
			>
			<view class="record-header">
				<view class="record-date">
					<text class="date-icon">📅</text>
					<text class="date-text">{{ record.check_time }}</text>
					<text v-if="!record.is_demo" class="real-data-badge">✓ 真实数据</text>
				</view>
				<view class="record-badges">
					<view class="record-status" :class="getVisitStatusMeta(record).className">
						<text>{{ getVisitStatusMeta(record).text }}</text>
					</view>
					<view class="record-status ai-status" :class="getAiStatusMeta(record).className">
						<text>{{ getAiStatusMeta(record).text }}</text>
					</view>
				</view>
			</view>
				
				<view class="record-content">
					<view class="content-left" v-if="record.img_url">
						<image :src="record.img_url" class="record-image" mode="aspectFill"></image>
					</view>
					<view class="content-main">
						<view class="record-info-item">
							<text class="info-label">检查项目</text>
							<text class="info-value">{{ record.check_project }}</text>
						</view>
						<view class="record-info-item">
							<text class="info-label">检查结果</text>
							<text class="info-value result-text">{{ record.imaging_finding_result }}</text>
						</view>
					</view>
					<view class="content-right">
						<view class="action-buttons">
							<view class="edit-btn" @click.stop="openEditForm(record, index)">
								<text class="btn-icon">✏️</text>
							</view>
							<view class="delete-btn" @click.stop="deleteRecord(record, index)">
								<text class="btn-icon">🗑️</text>
							</view>
							<view
								v-if="canGenerateAi(record)"
								class="ai-generate-btn"
								@click.stop="generateAiForRecord(record, index)"
							>
								<text class="btn-text">AI</text>
								<text class="arrow">↻</text>
							</view>
							<view class="view-detail-btn" @click.stop="toDetailPage(index)">
								<text class="btn-text">详情</text>
								<text class="arrow">→</text>
							</view>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 添加病历表单弹窗 -->
		<view class="modal-mask" v-if="showAddForm" @tap="closeAddForm">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">添加病历记录</text>
					<text class="close-btn" @tap="closeAddForm">✕</text>
				</view>
				
				<view class="modal-body">
					<view class="form-section">
						<text class="form-section-title">基本信息</text>
						
						<!-- 就诊日期 -->
						<view class="form-item">
							<text class="form-label">就诊日期<text class="required">*</text></text>
							<textarea 
								class="form-textarea-single" 
								v-model="newRecord.visit_date" 
								placeholder="例：2024-10-28 14:30"
								:auto-height="true"
								:maxlength="50"
							></textarea>
						</view>
						
						<!-- 科室选择 -->
						<view class="form-item">
							<text class="form-label">科室<text class="required">*</text></text>
							<view class="custom-selector" @click="showDepartmentPicker">
								<text class="selector-text" :class="{'placeholder': !newRecord.department}">
									{{ newRecord.department || '请选择科室' }}
								</text>
								<text class="selector-arrow">▼</text>
							</view>
						</view>
						
						<!-- 床号 -->
						<view class="form-item">
							<text class="form-label">床号</text>
							<textarea 
								class="form-textarea-single" 
								v-model="newRecord.bed_num" 
								placeholder="请输入床号"
								:auto-height="true"
								:maxlength="20"
							></textarea>
						</view>
						
						<!-- 检查项目选择 -->
						<view class="form-item">
							<text class="form-label">检查项目<text class="required">*</text></text>
							<view class="custom-selector" @click="showCheckProjectPicker">
								<text class="selector-text" :class="{'placeholder': !newRecord.check_project}">
									{{ newRecord.check_project || '请选择检查项目' }}
								</text>
								<text class="selector-arrow">▼</text>
							</view>
						</view>
						
						<!-- 检查部位选择 -->
						<view class="form-item">
							<text class="form-label">检查部位</text>
							<view class="custom-selector" @click="showPositionPicker">
								<text class="selector-text" :class="{'placeholder': !newRecord.position}">
									{{ newRecord.position || '请选择检查部位' }}
								</text>
								<text class="selector-arrow">▼</text>
							</view>
						</view>
					</view>
					
				<view class="form-section">
					<text class="form-section-title">检查结果</text>
					
					<view class="form-item">
						<text class="form-label">影像所见</text>
						<textarea class="form-textarea" v-model="newRecord.imaging_result" placeholder="请输入影像检查所见..." maxlength="500" />
					</view>
					
					<view class="form-item">
						<text class="form-label">诊断意见</text>
						<textarea class="form-textarea" v-model="newRecord.diagnosis" placeholder="请输入诊断意见..." maxlength="500" />
					</view>
				</view>
				
				<view class="form-section">
					<text class="form-section-title">医学影像（可选）</text>
					
					<view class="form-item">
						<text class="form-label">上传影像</text>
						<view class="upload-area-form">
							<button class="upload-btn-small" @tap="chooseImage" type="default" size="mini">选择图片</button>
							<text class="upload-hint-small">{{ uploadedImages.length > 0 ? `已选择${uploadedImages.length}张图片` : '未选择图片' }}</text>
						</view>
					</view>
					
					<view class="image-preview-list" v-if="uploadedImages.length > 0">
						<view class="preview-item" v-for="(img, index) in uploadedImages" :key="index">
							<image :src="img" class="preview-img" mode="aspectFill"></image>
							<text class="remove-img-btn" @tap="removeImage(index)">✕</text>
						</view>
					</view>
				</view>
			</view>
				
				<view class="modal-footer">
					<button class="modal-btn cancel-btn" @tap="closeAddForm">取消</button>
					<button class="modal-btn confirm-btn" @tap="submitNewRecord">保存</button>
				</view>
			</view>
		</view>
		
		<!-- 自定义选择器弹窗 -->
		<view class="selector-popup" v-if="showSelectorPopup" @tap="closeSelectorPopup">
			<view class="selector-content" @tap.stop>
				<view class="selector-header">
					<text class="selector-title">{{ selectorTitle }}</text>
					<text class="selector-close" @tap="closeSelectorPopup">✕</text>
				</view>
				<scroll-view scroll-y class="selector-list">
					<view 
						v-for="(item, index) in currentSelectorOptions" 
						:key="index"
						class="selector-item"
						@tap="selectOption(index)"
					>
						<text class="selector-item-text">{{ item }}</text>
					</view>
				</scroll-view>
			</view>
		</view>

		<!-- 编辑病历表单弹窗 -->
		<view class="modal-mask" v-if="showEditForm" @tap="closeEditForm">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">编辑病历记录</text>
					<text class="close-btn" @tap="closeEditForm">✕</text>
				</view>
				<view class="modal-body">
					<view class="form-section">
						<text class="form-section-title">基本信息</text>
						<view class="form-item">
							<text class="form-label">就诊日期</text>
							<textarea class="form-textarea-single" v-model="editRecord.visit_date" placeholder="例：2025-11-12 09:00" :auto-height="true" :maxlength="50" />
						</view>
						<view class="form-item">
							<text class="form-label">科室</text>
							<textarea class="form-textarea-single" v-model="editRecord.department" placeholder="请输入科室" :auto-height="true" :maxlength="100" />
						</view>
						<view class="form-item">
							<text class="form-label">床号</text>
							<textarea class="form-textarea-single" v-model="editRecord.bed_num" placeholder="请输入床号" :auto-height="true" :maxlength="50" />
						</view>
						<view class="form-item">
							<text class="form-label">检查项目</text>
							<textarea class="form-textarea-single" v-model="editRecord.check_project" placeholder="请输入检查项目" :auto-height="true" :maxlength="200" />
						</view>
						<view class="form-item">
							<text class="form-label">检查部位</text>
							<textarea class="form-textarea-single" v-model="editRecord.position" placeholder="请输入检查部位" :auto-height="true" :maxlength="200" />
						</view>
					</view>
					<view class="form-section">
						<text class="form-section-title">备注与诊断</text>
						<view class="form-item">
							<text class="form-label">备注</text>
							<textarea class="form-textarea" v-model="editRecord.notes" placeholder="备注/影像所见等..." maxlength="500" />
						</view>
						<view class="form-item">
							<text class="form-label">诊断意见</text>
							<textarea class="form-textarea" v-model="editRecord.diagnosis" placeholder="请输入诊断意见..." maxlength="500" />
						</view>
					</view>

					<!-- 编辑时补充CT图片（可选） -->
					<view class="form-section">
						<text class="form-section-title">补充CT图片（可选）</text>
						<view class="form-item">
							<text class="form-label">上传影像</text>
							<view class="upload-area-form">
								<button class="upload-btn-small" @tap="chooseEditCTImages" type="default" size="mini">选择图片</button>
								<text class="upload-hint-small">{{ editUploadedImages.length > 0 ? `已选择${editUploadedImages.length}张图片` : '未选择图片' }}</text>
							</view>
						</view>

						<view class="image-preview-list" v-if="editUploadedImages.length > 0">
							<view class="preview-item" v-for="(img, idx) in editUploadedImages" :key="idx">
								<image :src="img" class="preview-img" mode="aspectFill"></image>
								<text class="remove-img-btn" @tap="removeEditCTImage(idx)">✕</text>
							</view>
						</view>
					</view>
				</view>
				<view class="modal-footer">
					<button class="modal-btn cancel-btn" @tap="closeEditForm">取消</button>
					<button class="modal-btn confirm-btn" @tap="submitEditRecord">保存</button>
				</view>
			</view>
		</view>
		
		<!-- 底部导航栏 - 患者端 -->
		<bottom-nav-patient current="records"></bottom-nav-patient>
	</view>
</template>

<script>
import BottomNavPatient from '@/components/bottom_nav/BottomNavPatient.vue'

export default {
	name: "medicalRecord",
	components: {
		BottomNavPatient
	},
	async onLoad() {
		// 检查登录状态
		const authModule = await import('@/utils/auth.js')
		if (!authModule.requireAuth()) {
			return // 未登录会跳转，不需要继续执行
		}
		
		// 验证用户类型
		const userType = authModule.getCurrentUserType()
		if (userType !== 'patient') {
			uni.showToast({
				title: '此页面仅限患者访问',
				icon: 'none'
			})
			setTimeout(() => {
				uni.reLaunch({
					url: '/pages/selectIdentity/selectIdentity'
				})
			}, 1500)
			return
		}
		
	// 加载患者信息和病历数据
	await this.loadPatientInfo()
	await this.loadMedicalRecords()
},

async onShow() {
	// 每次页面显示时重新加载数据，确保数据是最新的且属于当前登录用户
	console.log('[onShow] 页面显示，重新加载数据')
	await this.loadPatientInfo()
	await this.loadMedicalRecords()
},

data() {
		return {
			loading: false,
			img_url: {
				girl: '/static/resource/girl.png',
				boy: '/static/resource/boy.png'
			},
			patient: {
				pat_id: '',
				name: '',
				gender: '男',
				age: 0,
				host_id: '',
				medical_record: []
			},
		// 添加病历表单相关
		showAddForm: false,
		newRecord: {
			visit_date: '',
			department: '',
			bed_num: '',
			check_project: '',
			position: '',
			imaging_result: '',
			diagnosis: ''
		},
		// 编辑病历表单相关
		showEditForm: false,
		editIndex: -1,
		editRecord: {
			id: null,
			visit_date: '',
			department: '',
			bed_num: '',
			check_project: '',
			position: '',
			notes: '',
			diagnosis: ''
		},
		// 选择器相关
		showSelectorPopup: false,
		selectorTitle: '',
		currentSelectorOptions: [],
		currentSelectorType: '',
		departmentOptions: ['神经内科', '神经外科', '肿瘤科', '放射科', '影像科', '急诊科', '内科', '外科', '其他'],
		checkProjectOptions: ['头颅MRI平扫', '头颅MRI增强', '头颅CT平扫', '头颅CT增强', '脑部MRI多序列扫描', '颅脑血管造影', '全脑灌注成像', '其他'],
		positionOptions: ['头颅', '颈部', '胸部', '腹部', '盆腔', '脊柱', '四肢', '其他'],
		currentPatientId: null,
		// 上传的图片列表
		uploadedImages: [],
		// 编辑时选择的CT图片
		editUploadedImages: []
		}
	},
	methods: {
		// 加载患者信息
		async loadPatientInfo() {
			try {
				// 检查是否是 patient1 用户，如果是则使用模拟患者信息
				const user = uni.getStorageSync('user')
				if (user && (user.username === 'patient1' || user.email === 'patient1@example.com')) {
					console.log('检测到 patient1 用户，使用模拟患者信息')
					this.patient = {
						pat_id: '110101198506150011',
						name: '王先生',
						gender: '男',
						age: 40,
						host_id: '1',
						medical_record: [] // 病历记录在 loadMedicalRecords 中加载
					}
					return
				}
				
				// 其他用户从后端获取真实数据
				const { patientAPI } = await import('@/utils/request.js')
				const response = await patientAPI.getMyProfile()
				console.log('患者信息:', response)
				
				if (response) {
					this.patient = {
						pat_id: response.id_card || response.id?.toString() || '',
						name: response.name || '',
						gender: response.gender === 'M' ? '男' : '女',
						age: response.age || 0,
						host_id: response.id?.toString() || '',
						medical_record: [] // 病历记录在 loadMedicalRecords 中加载
					}
				}
			} catch (error) {
				console.error('加载患者信息失败:', error)
				// 如果患者档案不存在，显示提示
				if (error.message && (error.message.includes('未找到') || error.message.includes('404'))) {
					uni.showToast({
						title: '请先完善患者档案',
						icon: 'none',
						duration: 2000
					})
				}
			}
		},
		
	// 加载医疗记录
	async loadMedicalRecords() {
		// 将 isPatient1 定义在方法顶部，确保 catch 块可以访问
		let isPatient1 = false
		
		try {
			this.loading = true
			
			// 检查是否是 patient1 用户
			const user = uni.getStorageSync('user')
			if (user && (user.username === 'patient1' || user.email === 'patient1@example.com')) {
				console.log('检测到 patient1 用户，先加载模拟数据')
				isPatient1 = true
					// 先设置模拟数据
					this.patient.medical_record = [
						{
							id: 'demo-1',
							check_time: '2024-10-11 10:02',
							department: '神经重症医学科(NICU)',
							bed_num: 18,
							report_time: '2024-10-11 10:02',
							check_project: '头颅MRI平扫',
							position: '105层',
							check_method: 'MRI扫描',
							img_url: '../../static/tumorPic/1.jpg',
							imaging_finding_result: '右侧颞叶可见异常信号影，大小约3.2×2.8cm，边界欠清晰，周围可见水肿带。建议进一步检查确诊。',
							diagnosis_opinion: '右侧颞叶占位性病变，考虑：1.胶质瘤可能性大 2.建议增强MRI进一步检查',
							is_demo: true
						},
						{
							id: 'demo-2',
							check_time: '2024-09-28 14:30',
							department: '神经外科',
							bed_num: 12,
							report_time: '2024-09-28 15:00',
							check_project: '头颅MRI增强',
							position: '120层',
							check_method: 'MRI增强扫描',
							img_url: '../../static/tumorPic/2.jpg',
							imaging_finding_result: '增强扫描显示病灶明显强化，呈环形强化特征，中心坏死区未见强化。',
							diagnosis_opinion: '结合平扫及增强表现，高度怀疑高级别胶质瘤，建议手术治疗。',
							is_demo: true
						}
					]
					// 继续执行，追加真实数据
				}
				
				// 其他用户从后端获取真实数据
				const { medicalRecordAPI } = await import('@/utils/request.js')
				const response = await medicalRecordAPI.getRecords()
				console.log('医疗记录列表:', response)
				
				// 处理响应数据（可能是数组或分页对象）
				let records = []
				if (Array.isArray(response)) {
					records = response
				} else if (response.results && Array.isArray(response.results)) {
					records = response.results
				} else if (response.medical_records && Array.isArray(response.medical_records)) {
					records = response.medical_records
				}
				
				// 导入配置（在map外部）
				let baseUrl = 'http://localhost:8766' // 默认值
				try {
					const envModule = await import('@/config/env.config.js')
					const config = envModule?.default || envModule?.ENV_CONFIG
					if (config && config.DJANGO_BASE_URL) {
						baseUrl = config.DJANGO_BASE_URL.replace('/api', '')
					}
				} catch (e) {
					console.warn('无法加载环境配置，使用默认baseUrl:', baseUrl)
				}

				// 转换数据格式以匹配前端显示
			const realRecords = records.map(record => {
				// 获取CT扫描信息（如果有）
				const ctScan = record.ct_scans && record.ct_scans.length > 0 ? record.ct_scans[0] : null
				
				// 格式化日期
				let checkTime = record.visit_date || record.created_at
				if (checkTime) {
					const date = new Date(checkTime)
					checkTime = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
				}
				
			// 处理图片URL（如果是相对路径，需要拼接后端地址）
			let imgUrl = '' // 无CT时不显示缩略图
			if (ctScan?.processed_image) {
				if (ctScan.processed_image.startsWith('http')) {
					imgUrl = ctScan.processed_image
				} else if (ctScan.processed_image.startsWith('/media/')) {
					imgUrl = `${baseUrl}${ctScan.processed_image}`
				} else {
					// Django ImageField返回相对路径，需要添加/media/前缀
					imgUrl = `${baseUrl}/media/${ctScan.processed_image}`
				}
			} else if (ctScan?.original_image) {
				if (ctScan.original_image.startsWith('http')) {
					imgUrl = ctScan.original_image
				} else if (ctScan.original_image.startsWith('/media/')) {
					imgUrl = `${baseUrl}${ctScan.original_image}`
				} else {
					// Django ImageField返回相对路径，需要添加/media/前缀
					imgUrl = `${baseUrl}/media/${ctScan.original_image}`
				}
			}
				
				return {
					id: record.id,
					check_time: checkTime,
					// 优先使用记录中的科室和检查项目信息
					department: record.department || record.doctor?.department || '未知科室',
					bed_num: record.bed_num || record.patient?.bed_num || '',
					report_time: checkTime,
					check_project: record.check_project || (ctScan ? `CT扫描 (${this.getScanModeText(ctScan.scan_mode)})` : '医疗检查'),
					position: record.position || ctScan?.tumor_location || '',
					check_method: ctScan ? 'CT扫描' : '常规检查',
					img_url: imgUrl,
					imaging_finding_result: record.notes || ctScan?.ai_analysis || ctScan?.doctor_review || record.diagnosis || '暂无检查结果',
					diagnosis_opinion: record.diagnosis || record.notes || '暂无诊断意见',
					// 保存完整记录数据，供详情页使用
					raw_data: record,
					is_demo: false  // 标记为真实数据
				}
			})
			
			// 如果是patient1，将真实数据追加到模拟数据后面
			if (isPatient1) {
				console.log(`追加 ${realRecords.length} 条真实病历记录到模拟数据`)
				this.patient.medical_record = [...this.patient.medical_record, ...realRecords]
			} else {
				this.patient.medical_record = realRecords
			}
			// Sort by date descending (newest first)
			this.patient.medical_record.sort((a, b) => {
				const da = new Date(a.check_time || a.raw_data?.visit_date || 0)
				const db = new Date(b.check_time || b.raw_data?.visit_date || 0)
				return db - da
			})
			
			console.log('处理后的病历记录:', this.patient.medical_record)
				
		} catch (error) {
			console.error('加载医疗记录失败:', error)
			// 如果是patient1，保留模拟数据
			// 如果不是patient1，清空记录
			if (!isPatient1) {
				this.patient.medical_record = []
			} else {
				console.log('patient1加载真实数据失败，保留模拟数据')
			}
		} finally {
			this.loading = false
		}
	},
		
		toDetailPage(index) {
			const record = this.patient.medical_record[index]
			if (!record) {
				return
			}
			
			// 保存当前选中的记录，供报告预览页面使用
			getCurrentPages()[getCurrentPages().length - 1].$vm.selectedRecord = record
			
			// 对于patient1的模拟数据，直接跳转到报告预览页面
			if (record.is_demo) {
				uni.navigateTo({
					url: '/pages/previewReport/previewReport?index=' + index
				})
			} else if (record.id && !record.is_demo) {
				// 真实数据，优先使用报告预览页面，传入recordId
				uni.navigateTo({
					url: `/pages/previewReport/previewReport?recordId=${record.id}`
				})
			} else {
				// 兼容旧的方式
				uni.navigateTo({
					url: '/pages/previewReport/previewReport?index=' + index
				})
			}
		},
		
		// 删除病历
		async deleteRecord(record, index) {
			// 如果是演示数据，直接从前端删除
			if (record.is_demo) {
				uni.showModal({
					title: '确认删除',
					content: '确定要删除这条病历记录吗？',
					success: (res) => {
						if (res.confirm) {
							this.patient.medical_record.splice(index, 1)
							uni.showToast({
								title: '删除成功',
								icon: 'success'
							})
						}
					}
				})
				return
			}
			
			// 真实数据，需要调用后端API删除
			if (!record.id) {
				uni.showToast({
					title: '无法删除：缺少记录ID',
					icon: 'none'
				})
				return
			}
			
			uni.showModal({
				title: '确认删除',
				content: '确定要删除这条病历记录吗？删除后无法恢复。',
				success: async (res) => {
					if (res.confirm) {
						try {
							uni.showLoading({
								title: '删除中...'
							})
							
							const { medicalRecordAPI } = await import('@/utils/request.js')
							await medicalRecordAPI.deleteRecord(record.id)
							
							// 从列表中移除
							this.patient.medical_record.splice(index, 1)
							
							uni.hideLoading()
							uni.showToast({
								title: '删除成功',
								icon: 'success'
							})
						} catch (error) {
							uni.hideLoading()
							console.error('删除病历失败:', error)
							uni.showToast({
								title: error.message || '删除失败',
								icon: 'none',
								duration: 2000
							})
						}
					}
				}
			})
		},
		
		getRecordScans(record) {
			return (record && record.raw_data && Array.isArray(record.raw_data.ct_scans))
				? record.raw_data.ct_scans
				: []
		},
		hasProcessedAi(record) {
			return this.getRecordScans(record).some(scan => !!scan.processed_image)
		},
		hasOriginalWithoutAi(record) {
			return this.getRecordScans(record).some(scan => !!scan.original_image && !scan.processed_image)
		},
		canGenerateAi(record) {
			return !record.is_demo && !!record.id && this.hasOriginalWithoutAi(record)
		},
		getVisitStatusMeta(record) {
			const raw = (record && record.raw_data) || {}
			const status = raw.status || ''
			const hasDoctor = !!(raw.doctor_name || raw.doctor || raw.is_assigned)

			if (status === 'completed') {
				return { text: '已完成', className: 'status-completed' }
			}
			if (status === 'cancelled') {
				return { text: '已取消', className: 'status-cancelled' }
			}
			if (status === 'processing' || hasDoctor) {
				return { text: '接诊中', className: 'status-processing' }
			}
			return { text: '已保存', className: 'status-saved' }
		},
		getAiStatusMeta(record) {
			const scans = this.getRecordScans(record)
			if (this.hasProcessedAi(record)) {
				return { text: 'AI已生成', className: 'status-ai-ready' }
			}
			if (this.hasOriginalWithoutAi(record)) {
				return { text: '待生成AI', className: 'status-ai-pending' }
			}
			if (scans.length === 0) {
				return { text: '未上传影像', className: 'status-ai-empty' }
			}
			return { text: 'AI待检查', className: 'status-ai-pending' }
		},
		async generateAiForRecord(record, index) {
			if (!this.canGenerateAi(record)) {
				uni.showToast({ title: '没有可生成的原始影像', icon: 'none' })
				return
			}
			try {
				uni.showLoading({ title: '生成AI分割图...', mask: true })
				const { medicalRecordAPI } = await import('@/utils/request.js')
				const response = await medicalRecordAPI.reanalyzeCTScans(record.id)
				uni.hideLoading()

				if (response.processed_count > 0) {
					uni.showToast({ title: 'AI分割图已生成', icon: 'success' })
					await this.loadMedicalRecords()
					return
				}

				uni.showToast({
					title: response.message || '没有可生成的影像',
					icon: 'none',
					duration: 2500
				})
			} catch (error) {
				uni.hideLoading()
				console.error('生成AI分割图失败:', error)
				uni.showToast({
					title: error.response?.data?.error || error.message || '生成失败',
					icon: 'none',
					duration: 3000
				})
			}
		},
		getScanModeText(scanMode) {
			const map = {
				'1': '平扫',
				'2': '增强',
				t1: 'T1',
				t2: 'T2',
				t1ce: 'T1CE',
				flair: 'FLAIR'
			}
			return map[scanMode] || scanMode || '其他'
		},
		// 打开编辑表单
		openEditForm(record, index) {
			if (record.is_demo) { // 演示数据不可编辑
				uni.showToast({ title: '演示记录不可编辑', icon: 'none' })
				return
			}
			this.editIndex = index
			this.editRecord = {
				id: record.id,
				visit_date: record.check_time || '',
				department: record.department || '',
				bed_num: record.bed_num || '',
				check_project: record.check_project || '',
				position: record.position || '',
				notes: record.raw_data?.notes || '',
				diagnosis: record.raw_data?.diagnosis || ''
			}
			this.showEditForm = true
		},
		closeEditForm() {
			this.showEditForm = false
			this.editIndex = -1
			this.editRecord = { id: null, visit_date: '', department: '', bed_num: '', check_project: '', position: '', notes: '', diagnosis: '' }
		},
		submitEditRecord: async function() {
			if (!this.editRecord.id) { uni.showToast({ title: '缺少记录ID', icon: 'none' }); return }
			try {
				uni.showLoading({ title: '保存中...' })
				const payload = {
					visit_date: this.editRecord.visit_date,
					department: this.editRecord.department,
					bed_num: this.editRecord.bed_num,
					check_project: this.editRecord.check_project,
					position: this.editRecord.position,
					notes: this.editRecord.notes,
					diagnosis: this.editRecord.diagnosis
				}
				const { medicalRecordAPI } = await import('@/utils/request.js')
				await medicalRecordAPI.updateRecord(this.editRecord.id, payload)

				// 如果选择了CT图片，则逐张上传
				if (this.editUploadedImages && this.editUploadedImages.length > 0) {
					for (let i = 0; i < this.editUploadedImages.length; i++) {
						const imagePath = this.editUploadedImages[i]
						try {
							await medicalRecordAPI.uploadCTScan(this.editRecord.id, { imagePath, scanMode: 't1' })
						} catch (uploadErr) {
							console.warn('上传CT图片失败（已忽略继续）:', uploadErr)
						}
					}
				}

				this.showEditForm = false
				this.editUploadedImages = []
				await this.loadMedicalRecords()
				uni.hideLoading()
				uni.showToast({ title: '保存成功', icon: 'success' })
			} catch (e) {
				uni.hideLoading()
				console.error('更新病历失败:', e)
				uni.showToast({ title: e.message || '保存失败', icon: 'none' })
			}
		},
		// 选择编辑时的CT图片
		chooseEditCTImages() {
			uni.chooseImage({
				count: 9,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					this.editUploadedImages = [...this.editUploadedImages, ...res.tempFilePaths]
					uni.showToast({ title: `已选择${res.tempFilePaths.length}张图片`, icon: 'success' })
				}
			})
		},
		// 移除编辑时选择的CT图片
		removeEditCTImage(index) {
			this.editUploadedImages.splice(index, 1)
		},
		goToHome() {
			// 返回身份选择页
			uni.reLaunch({
				url: '/pages/selectIdentity/selectIdentity'
			})
		},
		
	toIdentityPage() {
		uni.reLaunch({
			url: '/pages/selectIdentity/selectIdentity'
		})
	},
	
	// ========== 添加病历相关方法 ==========
	
	// 显示添加病历表单
	showAddRecordForm() {
		console.log('打开添加病历表单')
		this.showAddForm = true
		
		// 生成当前时间作为默认值
		const now = new Date()
		const year = now.getFullYear()
		const month = String(now.getMonth() + 1).padStart(2, '0')
		const day = String(now.getDate()).padStart(2, '0')
		const hours = String(now.getHours()).padStart(2, '0')
		const minutes = String(now.getMinutes()).padStart(2, '0')
		const defaultDateTime = `${year}-${month}-${day} ${hours}:${minutes}`
		
		// 初始化表单数据
		this.newRecord = {
			visit_date: defaultDateTime,
			department: '',
			bed_num: '',
			check_project: '',
			position: '',
			imaging_result: '',
			diagnosis: ''
		}
		
		// 清空上传的图片
		this.uploadedImages = []
	},
	
	// 关闭添加病历表单
	closeAddForm() {
		this.showAddForm = false
		this.newRecord = {
			visit_date: '',
			department: '',
			bed_num: '',
			check_project: '',
			position: '',
			imaging_result: '',
			diagnosis: ''
		}
		this.uploadedImages = [] // 清空上传的图片
	},
	
	// 显示科室选择器
	showDepartmentPicker() {
		console.log('点击了科室选择器')
		this.selectorTitle = '选择科室'
		this.currentSelectorOptions = this.departmentOptions
		this.currentSelectorType = 'department'
		this.showSelectorPopup = true
	},
	
	// 显示检查项目选择器
	showCheckProjectPicker() {
		console.log('点击了检查项目选择器')
		this.selectorTitle = '选择检查项目'
		this.currentSelectorOptions = this.checkProjectOptions
		this.currentSelectorType = 'check_project'
		this.showSelectorPopup = true
	},
	
	// 显示检查部位选择器
	showPositionPicker() {
		console.log('点击了检查部位选择器')
		this.selectorTitle = '选择检查部位'
		this.currentSelectorOptions = this.positionOptions
		this.currentSelectorType = 'position'
		this.showSelectorPopup = true
	},
	
	// 选择选项
	selectOption(index) {
		const selectedValue = this.currentSelectorOptions[index]
		this.newRecord[this.currentSelectorType] = selectedValue
		console.log('选择了:', this.currentSelectorType, selectedValue)
		this.closeSelectorPopup()
	},
	
	// 关闭选择器弹窗
	closeSelectorPopup() {
		this.showSelectorPopup = false
	},
	
	// 选择图片
	chooseImage() {
		console.log('点击了选择图片按钮')
		console.log('当前uploadedImages长度:', this.uploadedImages.length)
		
		uni.chooseImage({
			count: 9, // 最多选择9张
			sizeType: ['compressed'], // 压缩图
			sourceType: ['album', 'camera'], // 从相册或相机选择
			success: (res) => {
				console.log('图片选择成功！')
				console.log('选择的图片:', res.tempFilePaths)
				console.log('选择的图片数量:', res.tempFilePaths.length)
				
				// 添加到已上传列表
				this.uploadedImages = [...this.uploadedImages, ...res.tempFilePaths]
				
				console.log('更新后uploadedImages长度:', this.uploadedImages.length)
				console.log('更新后uploadedImages内容:', this.uploadedImages)
				
				uni.showToast({
					title: `已选择${res.tempFilePaths.length}张图片`,
					icon: 'success',
					duration: 1500
				})
			},
			fail: (err) => {
				console.error('选择图片失败:', err)
				uni.showToast({
					title: '选择图片失败',
					icon: 'none'
				})
			}
		})
	},
	
	// 删除图片
	removeImage(index) {
		this.uploadedImages.splice(index, 1)
	},
	
	// 提交新病历
	async submitNewRecord() {
		try {
			console.log('===== 开始提交新病历 =====')
			console.log('uploadedImages状态:', {
				length: this.uploadedImages.length,
				images: this.uploadedImages
			})
			
			// 表单验证
			if (!this.newRecord.visit_date) {
				uni.showToast({
					title: '请填写就诊日期',
					icon: 'none'
				})
				return
			}
			
			if (!this.newRecord.department) {
				uni.showToast({
					title: '请选择科室',
					icon: 'none'
				})
				return
			}
			
			if (!this.newRecord.check_project) {
				uni.showToast({
					title: '请选择检查项目',
					icon: 'none'
				})
				return
			}
			
			uni.showLoading({
				title: '保存中...'
			})
			
		console.log('开始保存病历...')
		console.log('当前患者信息:', this.patient)
		
		// 获取当前患者ID - 必须从后端获取，确保是当前登录用户的ID
		const user = uni.getStorageSync('user')
		console.log('当前用户:', user)
		
		let patient_id = null
		
		// 总是从后端获取当前登录患者的真实ID，避免使用缓存的错误数据
		console.log('从后端获取当前登录患者的档案...')
		try {
			const { patientAPI } = await import('@/utils/request.js')
			const profile = await patientAPI.getMyProfile()
			console.log('从后端获取的患者档案:', profile)
			patient_id = profile.id
			console.log('确认当前患者ID:', patient_id)
		} catch (profileError) {
			console.error('获取患者档案失败:', profileError)
			uni.hideLoading()
			uni.showModal({
				title: '提示',
				content: '未找到患者档案，请先完善个人信息',
				showCancel: false,
				success: () => {
					// 可以跳转到个人中心
					uni.navigateTo({
						url: '/pages/personalCenterPatient/personalCenterPatient'
					})
				}
			})
			return
		}
			
			// 再次检查patient_id
			if (!patient_id || patient_id === '' || patient_id === '0') {
				uni.hideLoading()
				uni.showModal({
					title: '无法保存',
					content: '无法获取患者ID，请确保已完善个人档案',
					showCancel: false
				})
				return
			}
			
		const { medicalRecordAPI } = await import('@/utils/request.js')
		
		// 格式化日期为ISO 8601格式
		let formattedDate = this.newRecord.visit_date
		if (formattedDate) {
			// 如果格式是 "2024-10-28 14:30"，转换为 "2024-10-28T14:30:00"
			formattedDate = formattedDate.replace(' ', 'T')
			// 如果没有秒，添加秒
			if (formattedDate.length === 16) { // YYYY-MM-DDTHH:MM
				formattedDate += ':00'
			}
		}
		
		// 准备数据
		const recordData = {
			patient_id: parseInt(patient_id),
			visit_date: formattedDate,
			department: this.newRecord.department || '',
			bed_num: this.newRecord.bed_num || '',
			check_project: this.newRecord.check_project || '',
			position: this.newRecord.position || '',
			diagnosis: this.newRecord.diagnosis || '',
			notes: this.newRecord.imaging_result || '',
			status: 'completed'
		}
			
			console.log('准备提交的数据:', recordData)
			
		// 创建医疗记录
		const createdRecord = await medicalRecordAPI.createRecord(recordData)
		console.log('创建成功的医疗记录:', createdRecord)
		
		// 如果有上传的图片，依次上传
		let uploadSuccessCount = 0
		if (this.uploadedImages && this.uploadedImages.length > 0) {
			console.log('开始上传图片，共', this.uploadedImages.length, '张')
			
			for (let i = 0; i < this.uploadedImages.length; i++) {
				try {
					const imagePath = this.uploadedImages[i]
					console.log(`上传第${i + 1}张图片:`, imagePath)
					
					// 使用uni.uploadFile上传图片
					const uploadResult = await new Promise((resolve, reject) => {
						const envConfigModule = require('@/config/env.config.js')
						const ENV_CONFIG = envConfigModule.default || envConfigModule
						const token = uni.getStorageSync('token')
						
						console.log(`准备上传，Token: ${token ? token.substring(0, 20) + '...' : 'null'}`)
						
						if (!token) {
							console.error('Token为空，无法上传图片')
							reject(new Error('未登录或Token已过期'))
							return
						}
						
						uni.uploadFile({
							url: `${ENV_CONFIG.DJANGO_BASE_URL}/medical-records/${createdRecord.id}/upload_ct_scan/`,
							filePath: imagePath,
							name: 'original_image',
							formData: {
								'scan_mode': 't1'  // 默认使用T1模式
							},
					header: {
						'Authorization': `Token ${token}`
						// 注意：不要手动设置Content-Type，uni.uploadFile会自动添加正确的multipart/form-data及boundary
					},
						success: (res) => {
							console.log(`第${i + 1}张图片上传响应:`, res)
							// 200和201都表示成功
							if (res.statusCode === 200 || res.statusCode === 201) {
								resolve(res)
							} else {
								console.error(`第${i + 1}张图片上传失败，状态码:`, res.statusCode)
								console.error('响应数据:', res.data)
								reject(new Error(`上传失败: ${res.statusCode}`))
							}
						},
							fail: (err) => {
								console.error(`第${i + 1}张图片上传失败:`, err)
								reject(err)
							}
						})
					})
					
					console.log(`第${i + 1}张图片上传完成`)
					uploadSuccessCount++
				} catch (uploadError) {
					console.error(`上传第${i + 1}张图片时出错:`, uploadError)
					uni.showToast({
						title: `第${i + 1}张图片上传失败`,
						icon: 'none',
						duration: 2000
					})
					// 继续上传下一张图片，不中断流程
				}
			}
			
			console.log(`所有图片上传完成，成功: ${uploadSuccessCount}/${this.uploadedImages.length}`)
			
			// 给后端一点时间处理图片
			await new Promise(resolve => setTimeout(resolve, 500))
		}
		
		uni.hideLoading()
		
		const successMsg = uploadSuccessCount > 0 
			? `保存成功，已上传${uploadSuccessCount}张图片` 
			: '保存成功'
		
		uni.showToast({
			title: successMsg,
			icon: 'success',
			duration: 2000
		})
		
		// 关闭表单
		this.closeAddForm()
		
		// 重新加载病历列表（确保获取最新的CT扫描数据）
		console.log('重新加载病历列表...')
		await this.loadMedicalRecords()
		console.log('病历列表加载完成')
			
		} catch (error) {
			uni.hideLoading()
			console.error('保存病历失败:', error)
			console.error('错误详情:', error.response ? error.response.data : error)
			
			let errorMsg = '保存失败'
			let errorDetails = []
			
			if (error.response && error.response.data) {
				console.log('[详细错误数据]:', JSON.stringify(error.response.data, null, 2))
				
				// 详细显示后端返回的错误
				if (typeof error.response.data === 'string') {
					errorMsg = error.response.data
				} else if (typeof error.response.data === 'object') {
					// 遍历所有字段错误
					Object.keys(error.response.data).forEach(key => {
						const value = error.response.data[key]
						if (Array.isArray(value)) {
							errorDetails.push(`${key}: ${value.join(', ')}`)
						} else {
							errorDetails.push(`${key}: ${value}`)
						}
					})
					
					if (errorDetails.length > 0) {
						errorMsg = errorDetails.join('\n')
					} else if (error.response.data.error) {
						errorMsg = error.response.data.error
					} else if (error.response.data.detail) {
						errorMsg = error.response.data.detail
					} else {
						errorMsg = JSON.stringify(error.response.data)
					}
				}
			} else if (error.message) {
				errorMsg = error.message
			}
			
			console.error('最终错误信息:', errorMsg)
			
			uni.showModal({
				title: '保存失败',
				content: errorMsg,
				showCancel: false
			})
		}
	}
}
}
</script>

<style scoped>
.medical-record-page {
	min-height: 100vh;
	background: var(--ds-bg);
	padding-bottom: 80px;
	font-family: var(--ds-font);
}

/* 导航栏 */
.custom-navbar {
	background: rgba(244,246,251,0.85);
	backdrop-filter: saturate(180%) blur(20px);
	-webkit-backdrop-filter: saturate(180%) blur(20px);
	padding: 52px 20px 14px;
	border-bottom: 1px solid var(--ds-hairline);
	position: sticky;
	top: 0;
	z-index: 100;
}

.navbar-content {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.navbar-right {
	width: 36px;
	height: 36px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: var(--ds-bg-sunken);
	border-radius: 12px;
	transition: all 0.18s;
}

.navbar-right:active {
	background: var(--ds-brand-soft);
	transform: scale(0.95);
}

.menu-icon {
	color: var(--ds-ink-2);
	font-size: 20px;
	font-weight: bold;
}

.navbar-center-full {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.navbar-title {
	font-size: 17px;
	font-weight: 700;
	color: var(--ds-ink-1);
	margin-bottom: 2px;
}

.navbar-subtitle {
	font-size: 10px;
	color: var(--ds-ink-4);
	font-family: var(--ds-font-mono);
	letter-spacing: 1px;
}

/* 患者信息卡片 */
.patient-info-card {
	margin: 18px 20px;
	background: var(--ds-grad-deep);
	border-radius: var(--ds-r-md);
	padding: 18px;
	display: flex;
	gap: 14px;
	box-shadow: var(--ds-shadow-md);
	overflow: hidden;
	position: relative;
	animation: ds-rise 0.5s var(--ds-ease) both;
	animation-delay: 0.05s;
}

.patient-info-card::before {
	content: '';
	position: absolute;
	top: -40px; right: -40px;
	width: 140px; height: 140px;
	background: radial-gradient(circle, rgba(0,194,215,0.4) 0%, transparent 70%);
	filter: blur(8px);
}

.patient-avatar-wrapper {
	flex-shrink: 0;
	position: relative;
	z-index: 1;
}

.patient-avatar {
	width: 76px;
	height: 76px;
	border-radius: 18px;
	border: 2px solid rgba(255, 255, 255, 0.25);
	
}

.patient-details {
	flex: 1;
	color: #fff;
	position: relative;
	z-index: 1;
}

.patient-name {
	font-size: 22px;
	font-weight: 800;
	display: block;
	margin-bottom: 12px;
	letter-spacing: 0.3px;
}

.patient-meta {
	display: flex;
	gap: 14px;
	flex-wrap: wrap;
}

.meta-item {
	display: flex;
	flex-direction: column;
	gap: 3px;
}

.meta-label {
	font-size: 10px;
	color: rgba(255,255,255,0.6);
	font-family: var(--ds-font-mono);
	letter-spacing: 0.5px;
	text-transform: uppercase;
}

.meta-value {
	font-size: 13px;
	font-weight: 600;
	color: #fff;
}

@keyframes ds-rise { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

/* 记录容器 */
.records-container {
	padding: 0 20px 20px;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 14px;
	padding: 0 4px;
}

.section-title {
	font-size: 18px;
	font-weight: 800;
	color: var(--ds-ink-1);
}

.record-count {
	font-size: 12px;
	color: var(--ds-ink-3);
}

.record-card {
	background: var(--ds-surface);
	border-radius: var(--ds-r-md);
	padding: 16px;
	margin-bottom: 12px;
	border: 1px solid var(--ds-hairline);
	box-shadow: var(--ds-shadow-sm);
	transition: all 0.18s var(--ds-ease);
	animation: ds-rise 0.5s var(--ds-ease) both;
}

.record-card:active {
	transform: scale(0.99);
	box-shadow: var(--ds-shadow-md);
}

.record-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12px;
	padding-bottom: 10px;
	border-bottom: 1px solid var(--ds-hairline);
}

.record-badges {
	display: flex;
	align-items: center;
	justify-content: flex-end;
	gap: 8px;
	flex-wrap: wrap;
}

.record-date {
	display: flex;
	align-items: center;
	gap: 5px;
	min-width: 0;
	flex-wrap: wrap;
}

.date-icon {
	font-size: 16px;
}

.date-text {
	font-size: 14px;
	color: #666666;
	font-weight: 500;
}

.real-data-badge {
	margin-left: 8px;
	padding: 2px 8px;
	background: var(--ds-grad-cyan);
	color: #ffffff;
	border-radius: var(--ds-r-pill);
	font-size: 10px;
	font-weight: 700;
	letter-spacing: 0.3px;
	box-shadow: 0 2px 8px rgba(0,194,215,0.25);
}

.record-status {
	padding: 4px 10px;
	border-radius: var(--ds-r-pill);
	font-size: 11px;
	font-weight: 700;
	white-space: nowrap;
}

.status-completed {
	background: rgba(31,184,119,0.13);
	color: var(--ds-success);
}

.status-processing {
	background: var(--ds-brand-soft);
	color: var(--ds-brand);
}

.status-saved {
	background: var(--ds-bg-sunken);
	color: var(--ds-ink-3);
}

.status-cancelled {
	background: var(--ds-bg-sunken);
	color: var(--ds-ink-4);
}

.status-ai-ready {
	background: var(--ds-cyan-soft);
	color: #008695;
}

.status-ai-pending {
	background: rgba(245,166,35,0.15);
	color: var(--ds-warning);
}

.status-ai-empty {
	background: var(--ds-bg-sunken);
	color: var(--ds-ink-4);
}

/* 记录内容 */
.record-content {
	display: flex;
	gap: 12px;
}

.content-left {
	flex-shrink: 0;
}

.record-image {
	width: 80px;
	height: 80px;
	border-radius: var(--ds-r-sm);
	background: var(--ds-bg-sunken);
}

.content-main {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.record-info-item {
	display: flex;
	flex-direction: column;
	gap: 3px;
}

.info-label {
	font-size: 11px;
	color: var(--ds-ink-3);
}

.info-value {
	font-size: 13px;
	color: var(--ds-ink-1);
}

.result-text {
	display: -webkit-box;
	-webkit-box-orient: vertical;
	-webkit-line-clamp: 2;
	line-clamp: 2;
	overflow: hidden;
	line-height: 1.4;
}

.content-right {
	flex-shrink: 0;
	display: flex;
	align-items: center;
}

.action-buttons {
	display: flex;
	align-items: center;
	gap: 10px;
	flex-wrap: wrap;
	justify-content: flex-end;
}

.edit-btn {
	width: 36px;
	height: 36px;
	background: var(--ds-bg-sunken);
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.18s;
}

.edit-btn:active {
	background: var(--ds-brand-soft);
	transform: scale(0.95);
}

.delete-btn {
	width: 36px;
	height: 36px;
	background: rgba(255,77,94,0.13);
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.18s;
}

.delete-btn:active {
	background: rgba(255,77,94,0.2);
	transform: scale(0.95);
}

.ai-generate-btn {
	background: var(--ds-grad-cyan);
	min-width: 48px;
	height: 36px;
	padding: 0 10px;
	border-radius: 10px;
	
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 1px;
	transition: all 0.18s;
}

.ai-generate-btn:active { transform: scale(0.95); }

.btn-icon { font-size: 16px; }

.view-detail-btn {
	background: var(--ds-grad-brand);
	padding: 8px 14px;
	border-radius: 10px;
	box-shadow: var(--ds-shadow-brand);
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 2px;
	transition: all 0.18s;
}

.view-detail-btn:active { transform: scale(0.95); }

.btn-text {
	color: #ffffff;
	font-size: 11px;
	font-weight: 600;
}

.arrow {
	color: #ffffff;
	font-size: 14px;
	transform: rotate(90deg);
}

/* 加载和空状态 */
.loading-container {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60px 20px;
}

.loading-spinner {
	width: 32px;
	height: 32px;
	border: 3px solid var(--ds-hairline);
	border-top-color: var(--ds-brand);
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

.loading-text {
	margin-top: 14px;
	color: var(--ds-ink-3);
	font-size: 13px;
}

.empty-state {
	text-align: center;
	padding: 60px 20px;
}

.empty-icon {
	font-size: 60px;
	display: block;
	margin-bottom: 15px;
	opacity: 0.5;
}

.empty-title {
	font-size: 18px;
	font-weight: bold;
	color: #333333;
	display: block;
	margin-bottom: 8px;
}

.empty-desc {
	font-size: 14px;
	color: #999999;
	display: block;
}

/* 动画 */
@keyframes fadeInDown {
	from {
		opacity: 0;
		transform: translateY(-20px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

@keyframes fadeInUp {
	from {
		opacity: 0;
		transform: translateY(20px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

@keyframes spin {
	from { transform: rotate(0deg); }
	to { transform: rotate(360deg); }
}

/* ========== 添加病历表单样式 ========== */

/* 头部按钮区域 */
.header-right {
	display: flex;
	align-items: center;
	gap: 10px;
}

.add-record-btn {
	background: linear-gradient(135deg, #0A5CFF 0%, #00C2D7 100%) !important;
	color: #ffffff !important;
	border: none !important;
	border-radius: 999px !important;
	padding: 8px 14px !important;
	font-size: 12px !important;
	height: auto !important;
	line-height: normal !important;
	font-weight: 600 !important;
	box-shadow: 0 4px 10px rgba(10,92,255,0.25) !important;
}

.add-record-btn::after {
	border: none !important;
}

/* 模态框样式 */
.modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.6);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 9999;
	padding: 20px;
}

.modal-content {
	background: var(--ds-surface);
	border-radius: var(--ds-r-md);
	width: 100%;
	max-width: 600px;
	max-height: 90vh;
	overflow: hidden;
	display: flex;
	flex-direction: column;
	animation: modalSlideUp 0.3s ease-out;
}

@keyframes modalSlideUp {
	from {
		opacity: 0;
		transform: translateY(50px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20px;
	border-bottom: 1px solid #f0f0f0;
}

.modal-title {
	font-size: 18px;
	font-weight: bold;
	color: #333333;
}

.close-btn {
	width: 30px;
	height: 30px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #f5f5f5;
	border-radius: 50%;
	color: #666666;
	font-size: 20px;
	cursor: pointer;
}

.close-btn:active {
	background: #e0e0e0;
}

.modal-body {
	flex: 1;
	overflow-y: auto;
	padding: 20px;
}

.form-section {
	margin-bottom: 25px;
}

.form-section-title {
	font-size: 15px;
	font-weight: 800;
	color: var(--ds-ink-1);
	margin-bottom: 14px;
	display: block;
	padding-bottom: 10px;
	border-bottom: 2px solid var(--ds-brand);
}

.form-item {
	margin-bottom: 18px;
}

.form-label {
	font-size: 14px;
	color: #666666;
	margin-bottom: 8px;
	display: block;
}

.required {
	color: #ff4d4f;
	margin-left: 3px;
}

/* 自定义选择器样式 */
.custom-selector {
	width: 100%;
	padding: 12px 15px;
	border: 1px solid #e0e0e0;
	border-radius: 8px;
	background: #ffffff;
	box-sizing: border-box;
	min-height: 44px;
	display: flex;
	justify-content: space-between;
	align-items: center;
	cursor: pointer;
	user-select: none;
	transition: all 0.3s;
}

.custom-selector:hover {
	border-color: #007aff;
	background-color: #f9f9f9;
}

.custom-selector:active {
	background-color: #f0f0f0;
}

.selector-text {
	flex: 1;
	font-size: 14px;
	color: #333333;
	pointer-events: none;
}

.selector-text.placeholder {
	color: #999999;
}

.selector-arrow {
	margin-left: 10px;
	font-size: 12px;
	color: #999999;
	pointer-events: none;
}

/* 选择器弹窗 */
.selector-popup {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	z-index: 9999;
	display: flex;
	align-items: flex-end;
}

.selector-content {
	width: 100%;
	max-height: 60vh;
	background: #ffffff;
	border-radius: 20px 20px 0 0;
	display: flex;
	flex-direction: column;
}

.selector-header {
	padding: 20px;
	border-bottom: 1px solid #f0f0f0;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.selector-title {
	font-size: 18px;
	font-weight: bold;
	color: #333333;
}

.selector-close {
	font-size: 24px;
	color: #999999;
	cursor: pointer;
	padding: 0 10px;
}

.selector-list {
	flex: 1;
	overflow-y: auto;
}

.selector-item {
	padding: 16px 20px;
	border-bottom: 1px solid #f5f5f5;
	cursor: pointer;
	transition: background-color 0.2s;
}

.selector-item:active {
	background-color: #f0f0f0;
}

.selector-item-text {
	font-size: 16px;
	color: #333333;
}

/* 单行textarea样式 - 用于输入框 */
.form-textarea-single {
	width: 100%;
	min-height: 44px;
	padding: 12px 15px;
	border: 1px solid #e0e0e0;
	border-radius: 8px;
	font-size: 14px;
	background: #ffffff;
	box-sizing: border-box;
	line-height: 20px;
}

.form-textarea {
	width: 100%;
	min-height: 100px;
	padding: 12px 15px;
	border: 1px solid #e0e0e0;
	border-radius: 8px;
	font-size: 14px;
	background: #fafafa;
	resize: vertical;
	box-sizing: border-box;
}

.form-textarea:focus {
	border-color: #007aff;
	background: #ffffff;
}

.modal-footer {
	display: flex;
	gap: 12px;
	padding: 15px 20px;
	border-top: 1px solid #f0f0f0;
}

.modal-btn {
	flex: 1;
	height: 44px;
	border-radius: 10px;
	font-size: 15px;
	font-weight: 500;
	border: none !important;
}

.modal-btn::after {
	border: none !important;
}

.cancel-btn {
	background: #f5f5f5 !important;
	color: #666666 !important;
}

.cancel-btn:active {
	background: #e0e0e0 !important;
}

.confirm-btn {
	background: linear-gradient(135deg, #0A5CFF 0%, #00C2D7 100%) !important;
	color: #ffffff !important;
	
}

.confirm-btn:active { transform: scale(0.97); }

/* 图片上传样式 */
.upload-area-form {
	display: flex;
	align-items: center;
	gap: 10px;
}

.upload-btn-small {
	background: var(--ds-brand-soft) !important;
	color: var(--ds-brand) !important;
	border: none !important;
	border-radius: 999px !important;
	padding: 8px 16px !important;
	font-size: 12px !important;
	height: auto !important;
	line-height: normal !important;
	font-weight: 600 !important;
}

.upload-btn-small::after {
	border: none !important;
}

.upload-hint-small {
	font-size: 13px;
	color: #999999;
}

.image-preview-list {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
	margin-top: 10px;
}

.preview-item {
	position: relative;
	width: 80px;
	height: 80px;
	border-radius: 8px;
	overflow: hidden;
	border: 1px solid #e0e0e0;
}

.preview-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.remove-img-btn {
	position: absolute;
	top: 2px;
	right: 2px;
	width: 20px;
	height: 20px;
	background: rgba(0, 0, 0, 0.6);
	color: #ffffff;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 14px;
	cursor: pointer;
}
</style>
