<template>
	<view class="preview_report">
		<!-- 头部导航栏 -->
		<view class="preview_report_header">
			<button class="navbar-back-btn" @tap="toReportPage" type="default" size="mini">← 返回</button>
			<text class="header-title">报告预览</text>
		</view>
		<!-- 这是身体 -->
		<view class="ct_report">
			<view class="ct_report_header">
				<p>天津市第一人民医院</p>
				<p>CT检查报告单</p>
			</view>
			
			<view class="ct_report_main">
				<view class="patient_info">
					<!-- 框框 -->
					<view class="patient_info_box">
						
						<div style="padding-top: 7px; display: flex;">
							<div style="float: left; width: 40%;">病人号：{{patient.pat_id || '未填写'}}</div>
							<div style="float: right; width: 60%;">检查日期：{{patient.check_time || '未填写'}}</div>
						</div>
						
						<hr style="width: 100%">
						<div style="display: flex;">
							<p>姓名：{{patient.name || '未填写'}}</p>
							<p style="padding-left: 8%;">性别：{{patient.gender || '未填写'}}</p>
							<p style="padding-left: 8%;">年龄：{{patient.age || ''}}{{patient.age ? '岁' : '未填写'}}</p>
						</div>
						<p>住院号：{{patient.host_id || '未填写'}}</p>
						
						<div style="display: flex;">
							<p>科室：{{patient.department || '未填写'}}</p>
							<p style="padding-left: 3%;">床号：{{patient.bed_num || '未填写'}}</p>
						</div>
						
						<p>报告日期：{{patient.report_time || '未填写'}}</p>
						<hr style="width: 100%">
						<p>检查项目：{{patient.check_project || '未填写'}}</p>
						<p style="padding-left: 80px;" v-if="patient.position">{{patient.position}}</p>
						
						
						
					<view class="ct_pic_result">
						<!-- 多图轮播 -->
						<view v-if="ct_pic_urls.length > 0" class="image-container">
							<!-- 左箭头 -->
							<view v-if="ct_pic_urls.length > 1 && currentImageIndex > 0" class="nav-arrow nav-arrow-left" @click="prevImage">
								<text class="arrow-icon">‹</text>
							</view>
							
							<swiper 
								class="ct_pic_swiper" 
								:current="currentImageIndex"
								:indicator-dots="ct_pic_urls.length > 1" 
								indicator-color="rgba(255, 255, 255, 0.5)"
								indicator-active-color="#fff"
								:autoplay="false" 
								:circular="false"
								:duration="300"
								@change="onSwiperChange"
							>
								<swiper-item v-for="(imgUrl, index) in ct_pic_urls" :key="index" class="swiper-item">
									<image :src="imgUrl" mode="aspectFill" class="ct_pic"></image>
								</swiper-item>
							</swiper>
							
							<!-- 右箭头 -->
							<view v-if="ct_pic_urls.length > 1 && currentImageIndex < ct_pic_urls.length - 1" class="nav-arrow nav-arrow-right" @click="nextImage">
								<text class="arrow-icon">›</text>
							</view>
							
							<!-- 图片计数器 -->
							<view v-if="ct_pic_urls.length > 1" class="image-counter">
								{{ currentImageIndex + 1 }} / {{ ct_pic_urls.length }}
							</view>
						</view>
						
						<!-- 单图显示（兼容旧逻辑） -->
						<image v-else-if="ct_pic_result_url" :src="ct_pic_result_url" mode="aspectFill" class="ct_pic"></image>
						<!-- 无AI分割图时不展示任何示例图片 -->
						<view v-else class="no-image-tip">
							<text class="no-image-title">暂无 AI 分割结果图</text>
							<text v-if="canRegenerateAi" class="no-image-desc">已检测到原始影像，可生成分割图</text>
							<view
								v-if="canRegenerateAi"
								class="reanalyze-mini-btn"
								:class="{ disabled: regeneratingAi }"
								@click="regenerateAiForCurrentRecord(false)"
							>
								<text>{{ regeneratingAi ? '生成中' : '生成AI图' }}</text>
							</view>
						</view>
					</view>
						<view>
							<p>影像结果：</p>
							<p>{{imaging_finding_result || '暂无检查结果'}}</p>
							<br>
						</view>
						<view>
							<p>影像诊断：</p>
							<p>{{imaging_diagnosis_result || '暂无诊断意见'}}</p>
						</view>
						<br>
						<hr>
						<view style="display: flex;">
							<div style="float: left; width: 60%">报告医师：{{doctor[0] || '待填写'}}</div>
							<div style="float: right; width: 40%; ">审核医师：{{doctor[1] || '待填写'}}</div>
						</view>
					</view>
				</view>
				
				
			</view>	
			<view class="ct_report_footer">
				
			</view>
		</view>
		<view class="ct_report_handle_button">
			<view class="save_report_button" @click="saveReport">
				<image src="../../static/button/saveReport.png" mode="aspectFill" class="button_icon_style"></image>
				<p class="button_text_style">保存报告</p>
			</view>
			<view class="send_report_button" v-if="!isFamily" @click="sendReport">
				<image src="../../static/button/sendReport.png" mode="aspectFill" class="button_icon_style"></image>
				<p class="button_text_style">{{ isDoctor ? '发送给病人' : '发送给医生' }}</p>
			</view>
		</view>
		<view style="height: 60px;">
			
		</view>
	</view>
</template>

<script>
export default{
	async onLoad(option){
		console.log("加载到了报告预览页", option)
		
		// 检查用户类型
		const authModule = await import('@/utils/auth.js')
		const userType = authModule.getCurrentUserType()
		this.isDoctor = userType === 'doctor'
		this.isFamily = userType === 'family'
		console.log('当前用户类型:', userType, '是否医生:', this.isDoctor, '是否家属:', this.isFamily)
		
		// 保存recordId和patientId用于后续操作
		if (option.recordId) {
			this.currentRecordId = option.recordId
		}
		if (option.pat_id) {
			this.currentPatientId = option.pat_id
		}
		
		// 支持多种参数传递方式
		if (option.index !== undefined) {
			// 从病历列表页面传递的index（用于patient1的模拟数据）
			await this.loadFromRecordIndex(parseInt(option.index))
		} else if (option.recordId) {
			// 从后端获取真实记录
			await this.loadFromRecordId(option.recordId)
		} else if (option.pat_id) {
			// 兼容旧的方式，尝试从病历记录中加载
			await this.loadFromPatientId(option.pat_id)
		} else {
			// 尝试从上一页获取传递的数据
			const pages = getCurrentPages()
			const prevPage = pages[pages.length - 2]
			if (prevPage && prevPage.data && prevPage.data.selectedRecord) {
				this.loadRecordData(prevPage.data.selectedRecord)
			}
		}
	},
	data(){
		return{
			isDoctor: false,  // 是否是医生用户
			isFamily: false,  // 是否是家属用户
			currentRecordId: null,  // 当前医疗记录ID
			currentPatientId: null,  // 当前患者ID
			patient:{
				pat_id:'',
				check_time:'',
				name:'',
				gender:'',
				age:'',
				host_id:'',
				department:'',
				bed_num:'',
				report_time:'',
				check_project:'',
				position:'',
			},
			imaging_finding_result:'',
			imaging_diagnosis_result:'',
			doctor:['', ''],
			ct_pic_result_url:'',  // 单图URL（兼容）
			ct_pic_urls:[],  // 多图URL数组
			currentImageIndex: 0,  // 当前显示的图片索引
			canRegenerateAi: false,
			missingAiCount: 0,
			regeneratingAi: false,
			autoRegenerateTried: false,
		}
	},
	methods:{
		// Swiper切换事件
		onSwiperChange(e) {
			this.currentImageIndex = e.detail.current
			console.log('切换到图片:', this.currentImageIndex + 1)
		},
		
		// 上一张图片
		prevImage() {
			if (this.currentImageIndex > 0) {
				this.currentImageIndex--
				console.log('上一张:', this.currentImageIndex + 1)
			}
		},
		
		// 下一张图片
		nextImage() {
			if (this.currentImageIndex < this.ct_pic_urls.length - 1) {
				this.currentImageIndex++
				console.log('下一张:', this.currentImageIndex + 1)
			}
		},

		formatMediaUrl(path, baseUrl) {
			if (!path) return ''
			if (path.startsWith('http')) return path
			if (path.startsWith('/media/')) return `${baseUrl}${path}`
			return `${baseUrl}/media/${path}`
		},
		
		toReportPage(){
			// 返回上一页（CT报告页面）
			uni.navigateBack({
				delta: 1
			})
		},
		
		// 从病历记录索引加载（用于patient1的模拟数据）
		async loadFromRecordIndex(index) {
			console.log('从记录索引加载:', index)
			
			// 获取当前用户的病历记录
			const user = uni.getStorageSync('user')
			if (user && (user.username === 'patient1' || user.email === 'patient1@example.com')) {
				// patient1 使用模拟数据
				const mockRecords = [
					{
						pat_id: '110101198506150011',
						check_time: '2024-10-11 10:02',
						name: '王先生',
						gender: '男',
						age: 40,
						host_id: '1',
						department: '神经重症医学科(NICU)',
						bed_num: 18,
						report_time: '2024-10-11 10:02',
						check_project: '头颅MRI平扫',
						position: '105层',
						imaging_finding_result: '右侧颞叶可见异常信号影，大小约3.2×2.8cm，边界欠清晰，周围可见水肿带。建议进一步检查确诊。',
						imaging_diagnosis_result: '右侧颞叶占位性病变，考虑：1.胶质瘤可能性大 2.建议增强MRI进一步检查',
						doctor: ['张医生', '李医生'],
						ct_pic_result_url: '../../static/tumorPic/1.jpg'
					},
					{
						pat_id: '110101198506150011',
						check_time: '2024-09-28 14:30',
						name: '王先生',
						gender: '男',
						age: 40,
						host_id: '1',
						department: '神经外科',
						bed_num: 12,
						report_time: '2024-09-28 15:00',
						check_project: '头颅MRI增强',
						position: '120层',
						imaging_finding_result: '增强扫描显示病灶明显强化，呈环形强化特征，中心坏死区未见强化。',
						imaging_diagnosis_result: '结合平扫及增强表现，高度怀疑高级别胶质瘤，建议手术治疗。',
						doctor: ['张医生', '李医生'],
						ct_pic_result_url: '../../static/tumorPic/2.jpg'
					}
				]
				
				if (mockRecords[index]) {
					this.loadRecordData(mockRecords[index])
				}
				return
			}
			
			// 其他用户从上一页获取数据
			const pages = getCurrentPages()
			const prevPage = pages[pages.length - 2]
			if (prevPage && prevPage.data && prevPage.data.patient && prevPage.data.patient.medical_record) {
				const record = prevPage.data.patient.medical_record[index]
				if (record) {
					this.loadRecordData(record)
				}
			}
		},
		
		// 从记录ID加载（真实数据）
		async loadFromRecordId(recordId, options = {}) {
			// 检查是否是patient1的模拟数据ID，demo-1和demo-2都是模拟数据，直接使用
			if (recordId === 'demo-1' || recordId === 'demo-2') {
				console.log('检测到patient1的模拟记录ID，使用模拟数据:', recordId)
				this.loadPatient1MockRecord(recordId)
				return
			}

			if (this.currentRecordId !== recordId) {
				this.autoRegenerateTried = false
			}
			
		try {
			const { medicalRecordAPI } = await import('@/utils/request.js')
			const record = await medicalRecordAPI.getRecord(recordId)
			console.log('获取到的医疗记录:', record)
			
			// 注意：不再强制为patient1使用模拟数据
			// 真实的recordId（数字ID）应该显示真实数据
			// 只有demo-1和demo-2才显示模拟数据（已在上面处理）
			
			// 格式化日期
			const formatDate = (dateStr) => {
				if (!dateStr) return ''
				const date = new Date(dateStr)
				return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
			}
			
			// 处理图片URL
			const envConfigModule = await import('@/config/env.config.js')
			const ENV_CONFIG = envConfigModule.default || envConfigModule
			const baseUrl = ENV_CONFIG.DJANGO_BASE_URL.replace('/api', '')
			console.log('后端基础URL:', baseUrl)
			
			// 处理所有CT扫描图片
			const imageUrls = []
			let firstCtScan = null  // 保存第一个CT扫描记录，用于后续字段填充
			let missingAiCount = 0
			
			if (record.ct_scans && record.ct_scans.length > 0) {
				console.log(`找到 ${record.ct_scans.length} 个CT扫描记录`)
				
				for (const ctScan of record.ct_scans) {
					if (!firstCtScan) {
						firstCtScan = ctScan  // 保存第一个CT扫描
					}
					
					let imgUrl = null
					
					// 只使用当前病历自己的AI分割结果图；没有processed_image就展示空状态
					if (ctScan.processed_image) {
						imgUrl = this.formatMediaUrl(ctScan.processed_image, baseUrl)
					} else if (ctScan.original_image) {
						missingAiCount += 1
					}
					
					if (imgUrl) {
						imageUrls.push(imgUrl)
						console.log(`CT扫描 ${imageUrls.length}:`, imgUrl)
					}
				}
			}
			
			let imgUrl = ''
			if (imageUrls.length > 0) {
				imgUrl = imageUrls[0]  // 第一张图作为主图（兼容旧逻辑）
				this.ct_pic_urls = imageUrls  // 保存所有图片URL
				console.log(`总共找到 ${imageUrls.length} 张图片`, this.ct_pic_urls)
			} else {
				this.ct_pic_urls = []
				console.log('该病历暂无AI分割结果图')
			}

			this.canRegenerateAi = missingAiCount > 0
			this.missingAiCount = missingAiCount
				
				// 保存患者ID和记录ID
				this.currentRecordId = recordId
				if (record.patient?.id) {
					this.currentPatientId = record.patient.id
				}

				if (
					imageUrls.length === 0 &&
					missingAiCount > 0 &&
					options.autoRegenerate !== false &&
					!this.autoRegenerateTried
				) {
					this.autoRegenerateTried = true
					await this.regenerateAiForCurrentRecord(true)
					return
				}
				
			const recordData = {
				pat_id: record.patient?.id_card || record.patient?.id || '',
				check_time: formatDate(record.visit_date || record.created_at),
				name: record.patient?.name || '',
				gender: record.patient?.gender === 'M' ? '男' : '女',
				age: record.patient?.age || '',
				host_id: record.patient?.id?.toString() || '',
				// 优先使用病历记录本身的字段
				department: record.department || record.doctor?.department || '',
				bed_num: record.bed_num || record.patient?.bed_num || '',
				report_time: formatDate(record.updated_at || record.created_at),
				// 优先使用病历记录中的检查项目
				check_project: record.check_project || (firstCtScan ? `CT扫描 (${this.getScanModeText(firstCtScan.scan_mode)})` : '医疗检查'),
				// 优先使用病历记录中的检查部位
				position: record.position || firstCtScan?.tumor_location || '',
				// 优先使用病历记录中的notes作为影像结果
				imaging_finding_result: record.notes || firstCtScan?.ai_analysis || firstCtScan?.doctor_review || record.diagnosis || '暂无检查结果',
				imaging_diagnosis_result: record.diagnosis || '暂无诊断意见',
				doctor: [
					record.doctor?.name || '待填写',
					record.doctor?.name || '待填写'  // 审核医师可以与报告医师相同，或从数据库获取
				],
				ct_pic_result_url: imgUrl
			}
				
				this.loadRecordData(recordData)
			} catch (error) {
				console.error('加载医疗记录失败:', error)
				uni.showToast({
					title: '加载报告失败',
					icon: 'none'
				})
			}
		},
		
		// 从患者ID加载（兼容旧方式）
		async loadFromPatientId(patId) {
			// 尝试从病历记录中查找
			const pages = getCurrentPages()
			const prevPage = pages[pages.length - 2]
			if (prevPage && prevPage.data && prevPage.data.patient && prevPage.data.patient.medical_record) {
				// 如果有病历记录，使用第一条
				const record = prevPage.data.patient.medical_record[0]
				if (record) {
					this.loadRecordData(record)
					return
				}
			}
			
			// 如果没有找到，显示错误
			uni.showToast({
				title: '未找到相关报告',
				icon: 'none'
			})
		},
		
		// 加载patient1的特定模拟记录
		loadPatient1MockRecord(recordId) {
			console.log('loadPatient1MockRecord 被调用，recordId:', recordId)
			const mockRecords = {
				'demo-1': {
					pat_id: '110101198506150011',
					check_time: '2024-10-11 10:02',
					name: '王先生',
					gender: '男',
					age: 40,
					host_id: '1',
					department: '神经重症医学科(NICU)',
					bed_num: 18,
					report_time: '2024-10-11 10:02',
					check_project: '头颅MRI平扫',
					position: '105层',
					imaging_finding_result: '右侧颞叶可见异常信号影，大小约3.2×2.8cm，边界欠清晰，周围可见水肿带。建议进一步检查确诊。',
					imaging_diagnosis_result: '右侧颞叶占位性病变，考虑：1.胶质瘤可能性大 2.建议增强MRI进一步检查',
					doctor: ['张医生', '李医生'],
					ct_pic_result_url: '../../static/tumorPic/1.jpg'
				},
				'demo-2': {
					pat_id: '110101198506150011',
					check_time: '2024-09-28 14:30',
					name: '王先生',
					gender: '男',
					age: 40,
					host_id: '1',
					department: '神经外科',
					bed_num: 12,
					report_time: '2024-09-28 15:00',
					check_project: '头颅MRI增强',
					position: '120层',
					imaging_finding_result: '增强扫描显示病灶明显强化，呈环形强化特征，中心坏死区未见强化。',
					imaging_diagnosis_result: '结合平扫及增强表现，高度怀疑高级别胶质瘤，建议手术治疗。',
					doctor: ['张医生', '李医生'],
					ct_pic_result_url: '../../static/tumorPic/2.jpg'
				}
			}
			
			const mockRecord = mockRecords[recordId]
			if (mockRecord) {
				console.log('找到模拟记录，准备加载数据:', mockRecord)
				// 保存当前记录ID和患者ID
				this.currentRecordId = recordId
				this.currentPatientId = mockRecord.host_id || '1'  // patient1的患者ID
				this.loadRecordData(mockRecord)
			} else {
				console.error('未找到匹配的模拟记录，recordId:', recordId)
			}
		},
		
	// 加载记录数据到页面
	loadRecordData(record) {
		console.log('加载记录数据:', record)
		console.log('图片URL字段值:')
		console.log('  - record.ct_pic_result_url:', record.ct_pic_result_url)
		console.log('  - record.img_url:', record.img_url)
		
		// 重置图片索引
		this.currentImageIndex = 0
		
		this.patient = {
			pat_id: record.pat_id || record.id_card || '',
			check_time: record.check_time || '',
			name: record.name || '',
			gender: record.gender || '',
			age: record.age || '',
			host_id: record.host_id || '',
			department: record.department || '',
			bed_num: record.bed_num || '',
			report_time: record.report_time || record.check_time || '',
			check_project: record.check_project || '',
			position: record.position || '',
		}
		this.imaging_finding_result = record.imaging_finding_result || record.imaging_result || ''
		this.imaging_diagnosis_result = record.imaging_diagnosis_result || record.diagnosis_opinion || record.diagnosis || ''
		
		if (record.doctor && Array.isArray(record.doctor)) {
			this.doctor = record.doctor
		} else if (record.doctor) {
			this.doctor = [record.doctor, record.doctor]
		} else {
			this.doctor = ['待填写', '待填写']
		}
		
		this.ct_pic_result_url = record.ct_pic_result_url || (record.is_demo ? record.img_url : '') || ''
		console.log('最终设置的图片URL:', this.ct_pic_result_url)
		console.log('ct_pic_urls数组:', this.ct_pic_urls)
			
			// 如果有host_id，保存为patientId
			if (record.host_id) {
				this.currentPatientId = record.host_id
			}
		},

		async regenerateAiForCurrentRecord(silent = false) {
			if (!this.currentRecordId || this.currentRecordId === 'demo-1' || this.currentRecordId === 'demo-2') {
				if (!silent) {
					uni.showToast({ title: '当前记录无法生成AI图', icon: 'none' })
				}
				return
			}
			if (this.regeneratingAi) return

			this.regeneratingAi = true
			try {
				if (!silent) {
					uni.showLoading({ title: '生成AI分割图...', mask: true })
				} else {
					uni.showLoading({ title: '正在补生成AI图...', mask: true })
				}

				const { medicalRecordAPI } = await import('@/utils/request.js')
				const response = await medicalRecordAPI.reanalyzeCTScans(this.currentRecordId)
				uni.hideLoading()

				if (response.processed_count > 0) {
					if (!silent) {
						uni.showToast({ title: 'AI分割图已生成', icon: 'success' })
					}
					await this.loadFromRecordId(this.currentRecordId, { autoRegenerate: false })
				} else {
					uni.showToast({
						title: response.message || '没有可生成的影像',
						icon: 'none',
						duration: 2500
					})
				}
			} catch (error) {
				uni.hideLoading()
				console.error('生成AI分割图失败:', error)
				uni.showToast({
					title: error.response?.data?.error || error.message || 'AI生成失败',
					icon: 'none',
					duration: 3000
				})
			} finally {
				this.regeneratingAi = false
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
		
		// 保存报告
		async saveReport() {
			try {
				uni.showLoading({
					title: '生成Word文档中...',
					mask: true
				})
				
				const { medicalRecordAPI } = await import('@/utils/request.js')
				const authModule = await import('@/utils/auth.js')
				const envConfigModule = await import('@/config/env.config.js')
				const ENV_CONFIG = envConfigModule.default || envConfigModule
				
				// 准备报告数据
				const reportData = {
					patient: {
						pat_id: this.patient.pat_id || '',
						check_time: this.patient.check_time || '',
						name: this.patient.name || '',
						gender: this.patient.gender || '',
						age: this.patient.age || '',
						host_id: this.patient.host_id || '',
						department: this.patient.department || '',
						bed_num: this.patient.bed_num || '',
						report_time: this.patient.report_time || '',
						check_project: this.patient.check_project || '',
						position: this.patient.position || ''
					},
					report: {
						imaging_finding_result: this.imaging_finding_result || '',
						imaging_diagnosis_result: this.imaging_diagnosis_result || '',
						doctor: this.doctor || ['', '']
					},
					user_type: this.isDoctor ? 'doctor' : (this.isFamily ? 'family' : 'patient')  // 添加用户类型
				}
				
				// 调用后端API生成Word文档
				const response = await medicalRecordAPI.generateWordReport(reportData)
				
				uni.hideLoading()
				
				// 显示保存成功信息
				const savePath = response.relative_path || response.file_path || `output/${response.filename}`
				uni.showModal({
					title: '报告生成成功',
					content: `Word文档已保存到服务器output文件夹中\n\n文件名：${response.filename}\n保存路径：${savePath}\n\n文件位置：${response.output_dir || 'output文件夹'}`,
					showCancel: false,
					confirmText: '确定'
				})
				
				uni.showToast({
					title: 'Word文档已保存到output文件夹',
					icon: 'success',
					duration: 3000
				})
				
				console.log('报告保存信息:', {
					filename: response.filename,
					file_path: response.file_path,
					relative_path: response.relative_path,
					output_dir: response.output_dir
				})
			} catch (error) {
				uni.hideLoading()
				console.error('保存报告失败:', error)
				let errorMsg = '生成失败'
				if (error.response && error.response.data && error.response.data.error) {
					errorMsg = error.response.data.error
				} else if (error.message) {
					errorMsg = error.message
				}
				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 3000
				})
			}
		},
		
		// 发送报告（医生发送给患者，患者发送给医生）
		async sendReport() {
			if (this.isDoctor) {
				await this.sendToPatient()
			} else {
				await this.sendToDoctor()
			}
		},
		
		// 发送报告给病人（医生端）
		async sendToPatient() {
			try {
				uni.showLoading({
					title: '发送中...',
					mask: true
				})
				
				const { notificationAPI, patientAPI } = await import('@/utils/request.js')
				
				// 检查是否是demo数据，如果是则需要查找真实的patient1记录
				let realPatientId = this.currentPatientId
				
				// 如果recordId是demo-1或demo-2，或者patient_id是"1"，说明是demo数据，需要查找真实的patient1
				if (this.currentRecordId === 'demo-1' || this.currentRecordId === 'demo-2' || 
				    this.currentPatientId === '1' || this.patient.pat_id === '110101198506150011') {
					console.log('检测到demo数据，查找patient1的真实记录')
					try {
						// 通过患者列表查找patient1
						const patients = await patientAPI.getPatients()
						const patientsList = Array.isArray(patients) ? patients : (patients.results || [])
						
						// 查找patient1：通过身份证号或用户名匹配
						const patient1 = patientsList.find(p => {
							const user = p.user || {}
							return (user.username === 'patient1' || 
							        p.id_card === '110101198506150011' ||
							        (p.name === '王先生' && p.id_card && p.id_card.includes('110101')))
						})
						
						if (patient1) {
							realPatientId = patient1.id || patient1._raw?.id
							console.log('找到patient1的真实ID:', realPatientId)
						} else {
							uni.hideLoading()
							uni.showToast({
								title: '未找到患者记录，无法发送通知',
								icon: 'none',
								duration: 3000
							})
							return
						}
					} catch (error) {
						console.error('查找患者失败:', error)
						uni.hideLoading()
						uni.showToast({
							title: '查找患者信息失败',
							icon: 'none',
							duration: 3000
						})
						return
					}
				}
				
				// 如果没有患者ID，尝试从host_id获取
				if (!realPatientId && this.patient.host_id) {
					realPatientId = this.patient.host_id
				}
				
				if (!realPatientId) {
					uni.hideLoading()
					uni.showToast({
						title: '缺少患者信息，无法发送',
						icon: 'none'
					})
					return
				}
				
				// 构建通知内容
				const title = `检查报告通知 - ${this.patient.check_project || '医疗检查'}`
				const content = `您的${this.patient.check_project || '医疗检查'}报告已生成，请及时查看。
				
患者信息：
- 姓名：${this.patient.name || '未填写'}
- 检查日期：${this.patient.check_time || '未填写'}
- 检查项目：${this.patient.check_project || '未填写'}

影像诊断：
${this.imaging_diagnosis_result || '暂无诊断意见'}

请及时查看完整报告。`
				
				await notificationAPI.sendToPatient({
					patient_id: realPatientId,
					medical_record_id: (this.currentRecordId && this.currentRecordId !== 'demo-1' && this.currentRecordId !== 'demo-2') 
						? this.currentRecordId 
						: null,  // demo数据不传递medical_record_id
					title: title,
					content: content
				})
				
				uni.hideLoading()
				uni.showToast({
					title: '已发送给患者',
					icon: 'success',
					duration: 2000
				})
			} catch (error) {
				uni.hideLoading()
				console.error('发送通知失败:', error)
				let errorMsg = '发送失败'
				if (error.response && error.response.data && error.response.data.error) {
					errorMsg = error.response.data.error
				} else if (error.message) {
					errorMsg = error.message
				}
				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 3000
				})
			}
		},
		
		// 发送报告给医生（患者端）
		async sendToDoctor() {
			try {
				uni.showLoading({
					title: '发送中...',
					mask: true
				})
				
				const { notificationAPI, medicalRecordAPI, doctorAPI } = await import('@/utils/request.js')
				
				let doctorUserId = null
				let doctorName = '医生'
				
				// 如果有医疗记录ID，尝试从医疗记录中获取接诊医生
				if (this.currentRecordId && this.currentRecordId !== 'demo-1' && this.currentRecordId !== 'demo-2') {
					try {
						const record = await medicalRecordAPI.getRecord(this.currentRecordId)
						console.log('获取到的医疗记录:', record)
						
						// 检查是否有接诊医生
						if (record.doctor && record.doctor.user && record.doctor.user.id) {
							doctorUserId = record.doctor.user.id
							doctorName = record.doctor.name || '医生'
							console.log('找到接诊医生:', doctorName, '用户ID:', doctorUserId)
						}
					} catch (error) {
						console.error('获取医疗记录失败:', error)
						// 继续执行，尝试获取doctor1
					}
				}
				
				// 如果没有接诊医生（模拟数据或未接诊），获取doctor1
				if (!doctorUserId) {
					console.log('未找到接诊医生，尝试获取doctor1')
					try {
						const doctors = await doctorAPI.getDoctors()
						const doctorsList = Array.isArray(doctors) ? doctors : (doctors.results || [])
						
						console.log('获取到的医生列表:', doctorsList)
						
						// 查找doctor1（用户名或邮箱为doctor1的医生）
						let doctor1 = doctorsList.find(d => 
							(d.user?.username === 'doctor1' || d.user?.email === 'doctor1@example.com') ||
							(d.username === 'doctor1' || d.email === 'doctor1@example.com')
						)
						
						// 如果找不到doctor1，使用第一个医生
						if (!doctor1 && doctorsList.length > 0) {
							doctor1 = doctorsList[0]
						}
						
						if (doctor1) {
							doctorUserId = doctor1.user?.id || doctor1.user_id || doctor1.id
							doctorName = doctor1.name || doctor1.user?.name || '医生'
							console.log('使用医生:', doctorName, '用户ID:', doctorUserId)
						} else {
							uni.hideLoading()
							uni.showToast({
								title: '暂无可用医生',
								icon: 'none',
								duration: 3000
							})
							return
						}
					} catch (error) {
						uni.hideLoading()
						console.error('获取医生信息失败:', error)
						uni.showToast({
							title: '获取医生信息失败',
							icon: 'none',
							duration: 3000
						})
						return
					}
				}
				
				if (!doctorUserId) {
					uni.hideLoading()
					console.error('无法获取医生用户ID')
					uni.showToast({
						title: '医生信息不完整',
						icon: 'none',
						duration: 3000
					})
					return
				}
				
				// 构建通知内容
				const title = `患者报告 - ${this.patient.check_project || '医疗检查'}`
				const content = `患者 ${this.patient.name || '未知'} 分享了检查报告：
				
检查信息：
- 检查日期：${this.patient.check_time || '未填写'}
- 检查项目：${this.patient.check_project || '未填写'}
- 患者年龄：${this.patient.age || '未填写'}岁

影像诊断：
${this.imaging_diagnosis_result || '暂无诊断意见'}

请查看完整报告。`
				
				// 使用通用聊天消息API发送
				await notificationAPI.sendChatMessage({
					recipient_id: doctorUserId,
					content: content
				})
				
				uni.hideLoading()
				uni.showToast({
					title: '已发送给医生',
					icon: 'success',
					duration: 2000
				})
			} catch (error) {
				uni.hideLoading()
				console.error('发送通知失败:', error)
				let errorMsg = '发送失败'
				if (error.response && error.response.data && error.response.data.error) {
					errorMsg = error.response.data.error
				} else if (error.message) {
					errorMsg = error.message
				}
				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 3000
				})
			}
		}
	}
}
</script>

<style scoped>
	@import 'previewReport.css'

</style>
