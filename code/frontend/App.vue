<style lang="scss">
	@import 'uview-ui/theme.scss';
</style>

<style>
	/* 全局设计系统:Clinical Precision 临床精密美学 */
	@import './styles/design-system.css';
</style>

<script>
	import { checkLoginAndRedirect } from '@/utils/auth.js'
	
	export default {
		onLaunch: function() {
			console.log('App Launch')
			
			// 检查登录状态
			// 如果已登录且token有效，可以在这里验证token
			// 暂时不自动跳转，让用户选择
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	
</style>