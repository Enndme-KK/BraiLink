<template>
	<view class="ds-app-header">
		<view class="ds-app-header__bg"></view>
		<view class="ds-app-header__inner">
			<view class="ds-app-header__back" v-show="show_quit" @click="goBack" hover-class="back-pressed">
				<text class="ds-app-header__back-char">‹</text>
			</view>
			<view v-else class="ds-app-header__back ds-app-header__back--ghost"></view>
			<text class="ds-app-header__title"><slot></slot></text>
			<view class="ds-app-header__placeholder"></view>
		</view>
	</view>
</template>

<script>
export default {
	name: 'AppHeader',
	props: {
		show_quit: { type: Boolean, default: false }
	},
	methods: {
		goBack() { uni.navigateBack({ delta: 1 }) }
	}
}
</script>

<style scoped>
.ds-app-header {
	position: sticky;
	top: 0;
	z-index: 100;
	font-family: var(--ds-font);
}
.ds-app-header__bg {
	position: absolute;
	top: 0; left: 0; right: 0; bottom: 0;
	background: rgba(244, 246, 251, 0.82);
	backdrop-filter: saturate(180%) blur(20px);
	-webkit-backdrop-filter: saturate(180%) blur(20px);
	border-bottom: 1px solid var(--ds-hairline);
}
.ds-app-header__inner {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 52px 16px 12px;
}
.ds-app-header__back {
	width: 36px; height: 36px;
	display: flex; align-items: center; justify-content: center;
	border-radius: 12px;
	transition: background 0.18s var(--ds-ease);
}
.ds-app-header__back--ghost { pointer-events: none; }
.back-pressed { background: var(--ds-brand-ghost); }
.ds-app-header__back-char {
	font-size: 32px;
	font-weight: 300;
	color: var(--ds-brand);
	line-height: 1;
	margin-top: -4px;
}
.ds-app-header__title {
	font-size: 17px;
	font-weight: 600;
	color: var(--ds-ink-1);
	letter-spacing: 0.2px;
	flex: 1;
	text-align: center;
}
.ds-app-header__placeholder { width: 36px; }
</style>
