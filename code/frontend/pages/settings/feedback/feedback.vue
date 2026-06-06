<template>
	<view class="page">
		<view class="navbar">
			<view class="navbar-bg"></view>
			<view class="navbar-inner">
				<view class="nav-back" @click="goBack" hover-class="back-pressed">
					<text class="back-char">‹</text>
				</view>
				<text class="nav-title">意见反馈</text>
				<view class="nav-action" :class="{ active: characterCount > 0 }" @click="submit">
					<text class="action-text">提交</text>
				</view>
			</view>
		</view>

		<view class="content">
			<view class="card ds-rise ds-d1">
				<textarea class="textbox" placeholder="说一下您的建议或遇到的问题..." placeholder-class="ph" v-model="suggest" maxlength="200" @input="countCharacters" />
				<view class="card-footer">
					<text class="footer-tip">您的反馈将帮助我们持续优化产品</text>
					<text class="counter ds-mono">{{ characterCount }} / 200</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() { return { suggest: '', characterCount: 0, submitting: false } },
	methods: {
		goBack() { uni.navigateBack({ delta: 1 }) },
		countCharacters() { this.characterCount = this.suggest.length },
		async submit() {
			if (this.submitting) return
			if (this.characterCount === 0) return
			this.submitting = true
			try {
				uni.showLoading({ title: '提交中...', mask: true })
				const { authAPI } = await import('@/utils/request.js')
				await authAPI.submitFeedback({ content: this.suggest.trim() })
				uni.hideLoading()
				uni.showToast({ title: '反馈成功', icon: 'success' })
				setTimeout(() => uni.navigateBack({ delta: 1 }), 800)
			} catch (e) {
				uni.hideLoading()
				const msg = (e && e.response && e.response.data && e.response.data.error) || e.message || '提交失败'
				uni.showToast({ title: msg, icon: 'none', duration: 2500 })
			} finally {
				this.submitting = false
			}
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
.nav-action { padding: 6px 14px; border-radius: var(--ds-r-pill); background: var(--ds-bg-sunken); transition: all 0.18s; }
.nav-action.active { background: var(--ds-grad-brand); box-shadow: var(--ds-shadow-brand); }
.action-text { font-size: 14px; font-weight: 600; color: var(--ds-ink-4); }
.nav-action.active .action-text { color: #fff; }

.content { padding: 16px 20px 0; }
.card { background: var(--ds-surface); border-radius: var(--ds-r-md); border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); padding: 16px; }
.textbox { width: 100%; min-height: 180px; font-size: 15px; line-height: 1.6; color: var(--ds-ink-1); background: transparent; border: none; }
.ph { color: var(--ds-ink-4); }
.card-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid var(--ds-hairline); margin-top: 12px; }
.footer-tip { font-size: 12px; color: var(--ds-ink-3); }
.counter { font-size: 12px; font-weight: 600; color: var(--ds-ink-4); letter-spacing: 0.5px; }
</style>
