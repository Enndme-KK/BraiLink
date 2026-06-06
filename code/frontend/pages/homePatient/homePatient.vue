<template>
	<view class="page">
		<view class="navbar" :style="{ opacity: navOpacity }">
			<view class="navbar-bg"></view>
			<view class="navbar-content">
				<text class="navbar-title">BraiLink</text>
			</view>
		</view>

		<!-- 顶部欢迎区 (深空蓝 + 神经网格 + 扫描线) -->
		<view class="hero ds-scanline ds-grid-bg">
			<view class="hero-glow"></view>
			<view class="hero-inner">
				<view class="hero-greet ds-rise ds-d1">
					<text class="hero-hello">{{ greetingText }}</text>
					<text class="hero-name">{{ patientInfo.name || '欢迎回来' }}</text>
				</view>
				<view class="hero-sub-row ds-rise ds-d2">
					<view class="sub-line"></view>
					<text class="hero-sub ds-mono">PATIENT · BRAIN AI</text>
					<view class="sub-line"></view>
				</view>
				<view class="hero-quick ds-rise ds-d3">
					<view class="quick-pill" @click="goRegistration">
						<view class="quick-ico">
							<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/><path d="M12 13v4M10 15h4"/></svg>
						</view>
						<text class="quick-text">挂诊</text>
					</view>
					<view class="quick-pill" @click="goAiChat">
						<view class="quick-ico">
							<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 20l1-4a8.5 8.5 0 0 1-1-4 8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5z"/></svg>
						</view>
						<text class="quick-text">AI 咨询</text>
					</view>
					<view class="quick-pill" @click="goRecords">
						<view class="quick-ico">
							<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2h-2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>
						</view>
						<text class="quick-text">病历</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 搜索 -->
		<view class="search-area ds-rise ds-d3">
			<view class="search-bar">
				<view class="search-ico">
					<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#69728C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.2-3.2"/></svg>
				</view>
				<input class="search-input" v-model="searchQuery" placeholder="搜索医学新闻" placeholder-class="ph" confirm-type="search" @confirm="handleSearchConfirm" @input="handleSearchInput" />
				<view class="search-clear" v-if="searchQuery" @click="clearSearch"><text class="clear-text">✕</text></view>
			</view>
		</view>

		<!-- Tabs -->
		<scroll-view class="tabs-scroll" scroll-x show-scrollbar="false">
			<view class="tab-pill" v-for="tab in topTabs" :key="tab" :class="{ active: activeTab === tab }" @click="selectTab(tab)">
				<text class="tab-text">{{ tab }}</text>
			</view>
		</scroll-view>

		<view class="content">
			<!-- 焦点新闻 -->
			<view class="hero-card ds-rise ds-d4" v-if="primaryNews" @click="openNews(primaryNews)">
				<image v-if="primaryNews.image" :src="primaryNews.image" class="hero-img" mode="aspectFill" />
				<view class="hero-overlay">
					<view class="hero-tag"><text class="hero-tag-text">今日精选</text></view>
					<text class="hero-title">{{ primaryNews.title }}</text>
					<text class="hero-meta">{{ primaryNews.source || '医学资讯' }} · {{ formatDate(primaryNews.date) }}</text>
				</view>
			</view>

			<view class="update-bar" v-if="lastUpdated">
				<view class="pulse-dot"></view>
				<text class="update-text ds-mono">UPDATED {{ formatDateTime(lastUpdated) }}</text>
			</view>

			<view class="news-group">
				<view class="news-item" v-for="(news, index) in secondaryNews" :key="index" @click="openNews(news)" hover-class="item-pressed">
					<view class="news-body">
						<text class="news-title">{{ news.title }}</text>
						<text class="news-summary">{{ news.summary }}</text>
						<text class="news-time">{{ news.source || '医学资讯' }} · {{ formatDate(news.date) }}</text>
					</view>
					<view class="news-thumb-wrap" v-if="news.image">
						<image :src="news.image" class="news-thumb" mode="aspectFill" />
					</view>
				</view>
			</view>

			<view class="loading-state" v-if="loadingNews"><view class="ds-spinner"></view></view>
			<view class="empty-state" v-if="!loadingNews && newsList.length === 0"><text class="empty-text">暂无医学新闻</text></view>

			<view style="height: 100px;"></view>
		</view>

		<BottomNavPatient current="home" />
	</view>
</template>

<script>
import BottomNavPatient from '@/components/bottom_nav/BottomNavPatient.vue'
import { homeAPI, patientAPI } from '@/utils/request.js'

export default {
	name: 'HomePatient',
	components: { BottomNavPatient },
	data() {
		return {
			scrollY: 0,
			loadingNews: false, newsList: [], lastUpdated: null, fromCache: false,
			topTabs: ['推荐', '科研', '诊疗', '政策', '健康'], activeTab: '推荐', searchQuery: '',
			categoryKeywords: { 科研: ['科研','研究','论文','突破'], 诊疗: ['诊疗','治疗','手术','诊断','临床'], 政策: ['政策','指南','通知','标准'], 健康: ['健康','养生','饮食','运动','预防'] },
			patientInfo: {}
		}
	},
	computed: {
		navOpacity() { return Math.min(this.scrollY / 100, 1) },
		greetingText() {
			const h = new Date().getHours()
			if (h < 6) return '夜深了，'
			if (h < 12) return '早上好，'
			if (h < 14) return '中午好，'
			if (h < 18) return '下午好，'
			return '晚上好，'
		},
		filteredNews() {
			let list = this.newsList
			if (this.activeTab !== '推荐') list = list.filter(i => (i.category || '推荐') === this.activeTab)
			const q = this.searchQuery.trim().toLowerCase()
			if (q) list = list.filter(i => `${i.title || ''} ${i.summary || ''}`.toLowerCase().includes(q))
			return list
		},
		primaryNews() { return this.filteredNews.length > 0 ? this.filteredNews[0] : null },
		secondaryNews() { return this.filteredNews.length <= 1 ? [] : this.filteredNews.slice(1) }
	},
	async onLoad() {
		const auth = await import('@/utils/auth.js')
		if (!auth.requireAuth()) return
		if (auth.getCurrentUserType() !== 'patient') { uni.showToast({ title: '此页面仅限患者访问', icon: 'none' }); setTimeout(() => uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' }), 1500); return }
		await this.loadPatientInfo(); await this.loadNews()
	},
	onPageScroll(e) { this.scrollY = e.scrollTop },
	methods: {
		async loadPatientInfo() { try { const r = await patientAPI.getMyProfile(); if (r) this.patientInfo = r } catch(e) {} },
		async loadNews(forceRefresh = false) {
			if (this.loadingNews) return; this.loadingNews = true
			try {
				const resp = await homeAPI.getMedicalNews(forceRefresh ? { refresh: true } : {})
				const env = (await import('@/config/env.config.js')).default
				const base = env.SERVER_URL || (env.DJANGO_BASE_URL ? env.DJANGO_BASE_URL.replace('/api','') : '')
				this.newsList = (resp.news || []).map(n => {
					const item = { ...n }
					if (item.image && item.image.trim() && !item.image.startsWith('http')) item.image = item.image.startsWith('/media/') ? `${base}${item.image}` : `${base}/media/${item.image}`
					else if (!item.image) item.image = ''
					item.summary = item.summary || ''; item.date = item.date || (resp.timestamp ? resp.timestamp.slice(0,10) : ''); item.category = this.detectCategory(item); return item
				})
				this.lastUpdated = resp.timestamp || null; this.fromCache = !!resp.from_cache
				if (forceRefresh) uni.showToast({ title: this.newsList.length > 0 ? '已更新' : '暂无新新闻', icon: this.newsList.length > 0 ? 'success' : 'none' })
			} catch(e) { uni.showToast({ title: e.message || '加载失败', icon: 'none' }) }
			finally { this.loadingNews = false }
		},
		handleSearchConfirm() { this.searchQuery = this.searchQuery.trim() },
		handleSearchInput(e) { if (typeof e === 'string') return; if (e?.detail?.value === '') this.searchQuery = '' },
		clearSearch() { this.searchQuery = '' },
		selectTab(tab) { this.activeTab = tab },
		openNews(news) { if (!news) return; uni.navigateTo({ url: '/pages/newsDetail/newsDetail', success: res => { try { res.eventChannel.emit('newsData', news) } catch(e) {} } }) },
		formatDate(d) { if (!d) return ''; const dt = new Date(d); return isNaN(dt.getTime()) ? d : `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}` },
		formatDateTime(iso) { if (!iso) return ''; const d = new Date(iso); return isNaN(d.getTime()) ? iso : `${d.getMonth()+1}-${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}` },
		detectCategory(n) { const t = `${n.title || ''} ${n.summary || ''}`.toLowerCase(); for (const [c, kws] of Object.entries(this.categoryKeywords)) { if (kws.some(k => k && t.includes(k.toLowerCase()))) return c } return '推荐' },
		goRegistration() { uni.reLaunch({ url: '/pages/registration/registration' }) },
		goAiChat() { uni.reLaunch({ url: '/pages/aiChat/aiChat' }) },
		goRecords() { uni.reLaunch({ url: '/pages/medicalRecord/medicalRecord' }) }
	}
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--ds-bg); font-family: var(--ds-font); padding-bottom: 80px; }

/* Sticky 顶栏 (滚动后显形) */
.navbar { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; opacity: 0; transition: opacity 0.18s var(--ds-ease); pointer-events: none; }
.navbar-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.navbar-content { position: relative; padding: 52px 20px 12px; text-align: center; }
.navbar-title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); letter-spacing: 0.5px; }

/* Hero 深空蓝 */
.hero { --ds-scan-h: 200px; position: relative; padding: 78px 24px 28px; background: linear-gradient(160deg, #0C1733 0%, #0A3A8C 55%, #0A5CFF 130%); overflow: hidden; }
.hero-glow { position: absolute; top: -60px; right: -60px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(0,194,215,0.45) 0%, transparent 70%); filter: blur(8px); }
.hero-inner { position: relative; }
.hero-greet { display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap; }
.hero-hello { font-size: 14px; color: rgba(255,255,255,0.75); }
.hero-name { font-size: 28px; font-weight: 800; color: #fff; letter-spacing: 0.5px; }
.hero-sub-row { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
.sub-line { width: 18px; height: 1px; background: rgba(255,255,255,0.35); }
.hero-sub { font-size: 10px; font-weight: 600; color: rgba(255,255,255,0.7); letter-spacing: 1.5px; }

.hero-quick { display: flex; gap: 8px; margin-top: 22px; }
.quick-pill { display: flex; align-items: center; gap: 6px; padding: 8px 14px; background: rgba(255,255,255,0.13); border: 1px solid rgba(255,255,255,0.18); border-radius: var(--ds-r-pill); transition: transform 0.18s var(--ds-ease), background 0.18s; }
.quick-pill:active { transform: scale(0.96); background: rgba(255,255,255,0.2); }
.quick-ico { width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; }
.quick-text { font-size: 13px; font-weight: 600; color: #fff; }

/* 搜索 */
.search-area { padding: 14px 20px 0; }
.search-bar { display: flex; align-items: center; gap: 8px; background: var(--ds-surface); border: 1px solid var(--ds-hairline); border-radius: var(--ds-r-sm); padding: 0 12px; height: 40px; box-shadow: var(--ds-shadow-sm); }
.search-ico { display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.search-input { flex: 1; font-size: 15px; color: var(--ds-ink-1); background: transparent; border: none; height: 40px; }
.ph { color: var(--ds-ink-4); }
.search-clear { width: 18px; height: 18px; border-radius: 50%; background: var(--ds-bg-sunken); display: flex; align-items: center; justify-content: center; }
.clear-text { font-size: 10px; color: var(--ds-ink-3); }

/* Tabs */
.tabs-scroll { white-space: nowrap; padding: 14px 20px 4px; }
.tabs-scroll::-webkit-scrollbar { display: none; }
.tab-pill { display: inline-block; padding: 7px 16px; border-radius: var(--ds-r-pill); margin-right: 8px; background: var(--ds-surface); border: 1px solid var(--ds-hairline); transition: all 0.2s var(--ds-ease); }
.tab-pill.active { background: var(--ds-grad-brand); border-color: transparent; box-shadow: var(--ds-shadow-brand); }
.tab-text { font-size: 14px; font-weight: 600; color: var(--ds-ink-2); letter-spacing: 0.3px; }
.tab-pill.active .tab-text { color: #fff; }

.content { padding: 12px 20px 0; }

/* 焦点新闻卡 */
.hero-card { position: relative; border-radius: var(--ds-r-md); overflow: hidden; height: 200px; margin-bottom: 16px; background: var(--ds-bg-sunken); box-shadow: var(--ds-shadow-md); }
.hero-img { width: 100%; height: 100%; }
.hero-overlay { position: absolute; bottom: 0; left: 0; right: 0; padding: 18px; background: linear-gradient(180deg, rgba(12,23,51,0), rgba(12,23,51,0.78)); }
.hero-tag { display: inline-block; padding: 3px 10px; border-radius: var(--ds-r-pill); background: rgba(0,194,215,0.85); margin-bottom: 8px; }
.hero-tag-text { font-size: 11px; font-weight: 700; color: #fff; letter-spacing: 0.5px; }
.hero-title { display: block; font-size: 18px; font-weight: 700; color: #fff; line-height: 1.4; margin-bottom: 6px; }
.hero-meta { font-size: 12px; color: rgba(255,255,255,0.75); }

.update-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; padding-left: 4px; }
.pulse-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--ds-success); box-shadow: 0 0 0 0 rgba(31,184,119,0.5); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(31,184,119,0.5); } 70% { box-shadow: 0 0 0 6px rgba(31,184,119,0); } 100% { box-shadow: 0 0 0 0 rgba(31,184,119,0); } }
.update-text { font-size: 10px; font-weight: 600; color: var(--ds-ink-3); letter-spacing: 1px; }

/* 列表 */
.news-group { background: var(--ds-surface); border-radius: var(--ds-r-md); overflow: hidden; margin-bottom: 16px; border: 1px solid var(--ds-hairline); }
.news-item { display: flex; padding: 14px 16px; gap: 12px; transition: background 0.15s; }
.news-item + .news-item { border-top: 1px solid var(--ds-hairline); }
.item-pressed { background: var(--ds-bg-sunken); }
.news-body { flex: 1; min-width: 0; }
.news-title { display: block; font-size: 15px; font-weight: 600; color: var(--ds-ink-1); line-height: 1.45; margin-bottom: 4px; -webkit-line-clamp: 2; overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; }
.news-summary { display: block; font-size: 13px; color: var(--ds-ink-3); margin-bottom: 6px; -webkit-line-clamp: 1; overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; }
.news-time { font-size: 11px; color: var(--ds-ink-4); font-family: var(--ds-font-mono); letter-spacing: 0.3px; }
.news-thumb-wrap { flex-shrink: 0; }
.news-thumb { width: 76px; height: 56px; border-radius: var(--ds-r-xs); background: var(--ds-bg-sunken); }

.loading-state { padding: 40px 0; display: flex; justify-content: center; }
.empty-state { padding: 60px 20px; text-align: center; }
.empty-text { font-size: 14px; color: var(--ds-ink-4); }
</style>
