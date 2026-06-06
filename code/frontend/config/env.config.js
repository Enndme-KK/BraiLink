// 环境配置文件
// 根据不同环境配置不同的 API 地址

// 后端 Django 监听端口为 8000。
// 浏览器(H5)预览用 localhost 即可;打包成 APK 真机运行时,
// 把 localhost 换成后端服务器的实际 IP(手机需能访问到该地址),只改这一行即可。
const SERVER_HOST = 'http://localhost:8000'

// 开发环境配置
const development = {
	// 统一使用腾讯云服务器，避免真机/模拟器访问 127.0.0.1 失败
	DJANGO_BASE_URL: `${SERVER_HOST}/api`,
	// 服务器根地址（用于访问媒体文件）
	SERVER_URL: SERVER_HOST,
	// ML 服务地址 - 已整合到 Django
	FLASK_ML_URL: `${SERVER_HOST}/api/ml`,
	// 环境标识
	ENV: 'development'
}

// 生产环境配置 - 服务器部署
const production = {
	DJANGO_BASE_URL: `${SERVER_HOST}/api`,
	// 服务器根地址（用于访问媒体文件）
	SERVER_URL: SERVER_HOST,
	// ML 服务地址 - 已整合到 Django
	FLASK_ML_URL: `${SERVER_HOST}/api/ml`,
	// 环境标识
	ENV: 'production'
}

// 测试环境配置
const testing = {
	// 测试环境也先统一走当前服务器，避免切环境后接口失效
	DJANGO_BASE_URL: `${SERVER_HOST}/api`,
	// 服务器根地址（用于访问媒体文件）
	SERVER_URL: SERVER_HOST,
	// ML 服务地址 - 已整合到 Django
	FLASK_ML_URL: `${SERVER_HOST}/api/ml`,
	// 环境标识
	ENV: 'testing'
}

// 根据当前环境返回对应配置
// 默认使用开发环境，可以通过修改这里切换环境
// 在实际部署时，建议通过环境变量或打包参数来控制

// 获取当前环境 - 你可以根据需要修改这里
const getCurrentEnv = () => {
	// 方法1: 直接返回指定环境（最简单）
	// return development; // 开发环境
	// return production;  // 生产环境

	// 方法2: 通过 process.env.NODE_ENV 判断（推荐）
	// #ifdef H5
	if (process.env.NODE_ENV === 'production') {
		return production;
	} else if (process.env.NODE_ENV === 'testing') {
		return testing;
	}
	return development;
	// #endif

	// #ifndef H5
	// App端（Android/iOS）直接使用生产环境连接服务器
	return production;
	// #endif
}

// 导出当前环境配置
export default getCurrentEnv();

// 也可以导出所有配置，方便调试
export {
	development,
	production,
	testing
}

