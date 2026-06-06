<template>
	<view class="ai-fab" @click="openAiChat" @touchstart="onTouchStart" @touchmove.stop.prevent="onTouchMove" @touchend="onTouchEnd" :style="fabStyle">
		<view class="fab-inner">
			<text class="fab-icon">AI</text>
		</view>
	</view>
</template>

<script>
export default {
	name: 'AiFab',
	data() {
		return {
			x: -1,
			y: -1,
			startX: 0,
			startY: 0,
			moveX: 0,
			moveY: 0,
			dragging: false,
			screenW: 375,
			screenH: 700
		}
	},
	computed: {
		fabStyle() {
			if (this.x < 0 || this.y < 0) return 'right: 16px; bottom: 140px;'
			return `left: ${this.x}px; top: ${this.y}px;`
		}
	},
	mounted() {
		const sys = uni.getSystemInfoSync()
		this.screenW = sys.windowWidth
		this.screenH = sys.windowHeight
		// 默认位置：右下角
		this.x = this.screenW - 60 - 16
		this.y = this.screenH - 140
	},
	methods: {
		openAiChat() {
			if (this.dragging) return
			uni.navigateTo({ url: '/pages/aiChat/aiChat' })
		},
		onTouchStart(e) {
			this.dragging = false
			const touch = e.touches[0]
			this.startX = touch.clientX
			this.startY = touch.clientY
			this.moveX = this.x
			this.moveY = this.y
		},
		onTouchMove(e) {
			const touch = e.touches[0]
			const dx = touch.clientX - this.startX
			const dy = touch.clientY - this.startY
			if (Math.abs(dx) > 5 || Math.abs(dy) > 5) this.dragging = true
			let nx = this.moveX + dx
			let ny = this.moveY + dy
			// 边界限制
			nx = Math.max(0, Math.min(nx, this.screenW - 56))
			ny = Math.max(60, Math.min(ny, this.screenH - 80))
			this.x = nx
			this.y = ny
		},
		onTouchEnd() {
			// 吸附到左右边缘
			const mid = this.screenW / 2
			if (this.x + 28 < mid) {
				this.x = 12
			} else {
				this.x = this.screenW - 56 - 12
			}
			// 延迟重置 dragging 防止触发 click
			setTimeout(() => { this.dragging = false }, 100)
		}
	}
}
</script>

<style scoped>
.ai-fab {
	position: fixed;
	z-index: 9990;
	width: 56px;
	height: 56px;
	transition: left 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94), top 0s;
}
.fab-inner {
	width: 56px;
	height: 56px;
	border-radius: 50%;
	background: var(--ds-grad-brand);
	box-shadow: 0 4px 16px rgba(10, 92, 255, 0.35), 0 2px 6px rgba(0,0,0,0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	transition: transform 0.2s, box-shadow 0.2s;
}
.fab-inner:active {
	transform: scale(0.92);
	box-shadow: 0 2px 8px rgba(10, 92, 255, 0.25);
}
.fab-icon {
	font-size: 18px;
	font-weight: 800;
	color: #fff;
	letter-spacing: 0.5px;
}
</style>
