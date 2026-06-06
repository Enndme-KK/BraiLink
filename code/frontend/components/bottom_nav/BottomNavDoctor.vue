<template>
	<view>
		<ai-fab />
		<view class="bottom-nav">
			<view class="nav-container">
			<view
				class="nav-item"
				v-for="(item, index) in navItems"
				:key="index"
				:class="{active: currentPage === item.path}"
				@click="navigateTo(item.path)"
			>
				<view class="nav-dot"></view>
				<view class="nav-icon" v-html="item.svg"></view>
				<text class="nav-text">{{ item.label }}</text>
			</view>
		</view>
	</view>
	</view>
</template>

<script>
const ICONS = {
	home: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9.5 21v-6h5v6"/></svg>',
	patients: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="3.5"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.3a4 4 0 0 1 0 7.4"/></svg>',
	scan: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M11 7v8M7 11h8" opacity=".55"/><path d="m20 20-3.2-3.2"/></svg>',
	chat: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 20l1-4a8.5 8.5 0 0 1-1-4 8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5z"/></svg>',
	profile: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M5 21v-1a7 7 0 0 1 14 0v1"/></svg>'
}
import AiFab from '@/components/ai_fab/AiFab.vue'
export default {
	name: 'BottomNavDoctor',
	components: { AiFab },
	props: {
		current: {
			type: String,
			default: 'home'
		}
	},
	data() {
		return {
			currentPage: this.current,
			navItems: [
				{ path: 'home', svg: ICONS.home, label: '首页', url: '/pages/homeDoctor/homeDoctor' },
				{ path: 'patients', svg: ICONS.patients, label: '患者', url: '/pages/managePatients/managePatients' },
				{ path: 'scan', svg: ICONS.scan, label: '扫描', url: '/pages/ctScanner/ctScanner' },
				{ path: 'messages', svg: ICONS.chat, label: '消息', url: '/pages/settings/sysNotice/sysNotice' },
				{ path: 'profile', svg: ICONS.profile, label: '我的', url: '/pages/personalCenter/personalCenter' }
			]
		}
	},
	methods: {
		navigateTo(path) {
			if (this.currentPage === path) return

			const item = this.navItems.find(i => i.path === path)
			if (item) {
				uni.reLaunch({
					url: item.url
				})
			}
		}
	}
}
</script>

<style scoped>
.bottom-nav {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background: rgba(255,255,255,0.92);
	backdrop-filter: saturate(180%) blur(20px);
	-webkit-backdrop-filter: saturate(180%) blur(20px);
	border-top: 1px solid var(--ds-hairline);
	box-shadow: 0 -4px 20px rgba(12, 23, 51, 0.06);
	z-index: 999;
	padding-bottom: env(safe-area-inset-bottom);
}

.nav-container {
	display: flex;
	justify-content: space-around;
	align-items: center;
	height: 58px;
}

.nav-item {
	position: relative;
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 3px;
	color: var(--ds-ink-4);
	transition: color 0.25s var(--ds-ease);
}

.nav-item:active { opacity: 0.6; }

.nav-dot {
	position: absolute;
	top: 4px;
	width: 4px; height: 4px;
	border-radius: 50%;
	background: var(--ds-brand);
	opacity: 0;
	transform: scale(0.4);
	transition: opacity 0.25s var(--ds-ease), transform 0.25s var(--ds-ease-spring);
}
.nav-item.active .nav-dot { opacity: 1; transform: scale(1); }

.nav-icon {
	width: 24px; height: 24px;
	display: flex; align-items: center; justify-content: center;
	transition: transform 0.25s var(--ds-ease-spring);
}

.nav-item.active { color: var(--ds-brand); }
.nav-item.active .nav-icon { transform: translateY(-1px) scale(1.08); }

.nav-text {
	font-size: 11px;
	font-weight: 500;
	transition: font-weight 0.25s;
}
.nav-item.active .nav-text { font-weight: 700; }
</style>

