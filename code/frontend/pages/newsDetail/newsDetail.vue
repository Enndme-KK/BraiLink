<template>
  <view class="news-detail-page">
    <view class="header">
      <view class="back" @click="goBack">← 返回</view>
      <text class="title">{{ headerTitle }}</text>
      <view v-if="news && news.url" class="open-btn" @click="openInBrowser">在浏览器打开</view>
    </view>

    <!-- 当需要外链原页时，使用 web-view 独占页面高度，避免嵌套滚动造成空白遮挡 -->
    <view v-if="isExternal" class="web-container">
      <web-view class="detail-webview" :src="news && news.url ? news.url : ''"></web-view>
    </view>
    <!-- 其余情况保留原有滚动容器与富文本渲染 -->
    <scroll-view v-else class="content" scroll-y>
      <view class="news-card" v-if="news">
        <text class="news-title">{{ news.title }}</text>
        <view class="meta">
          <text class="source">{{ news.source || '医学资讯' }}</text>
          <text class="date">{{ formatDate(news.date) }}</text>
        </view>

        <view class="news-body">
          <!-- 优先显示content字段作为正文 -->
          <rich-text v-if="news.content" :nodes="sanitizeContent(news.content)"></rich-text>
          <!-- 如果有安全处理后的HTML，显示它 -->
          <rich-text v-else-if="news._safeHtml" :nodes="news._safeHtml"></rich-text>
          <!-- 最后兜底显示摘要 -->
          <rich-text v-else-if="news.summary" :nodes="sanitizeContent(news.summary)"></rich-text>
          <view v-else>
            <text class="no-content">暂无详细内容</text>
          </view>
        </view>
      </view>

      <view v-else class="loading-placeholder">
        <text>正在加载新闻...</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      news: null,
      loadingExternal: false,
      externalFetchFailed: false
    }
  },
  computed: {
    headerTitle() {
      return (this.news && this.news.title) ? this.news.title : '新闻详情'
    },
    // 是否直接显示外链页面
    isExternal() {
      const n = this.news
      return !!(n && !n.content && !n._safeHtml && n.url)
    }
  },
  onLoad() {
    // 通过 eventChannel 获取传递的数据
    const eventChannel = this.getOpenerEventChannel && this.getOpenerEventChannel()
    if (eventChannel && eventChannel.on) {
      eventChannel.on('newsData', (data) => {
        this.news = data || null
      })
    }

    // 兼容：如果没有通过 eventChannel 传入，尝试从 options 中读取 url 或 id
    const options = this.$page && this.$page.query ? this.$page.query : (this.$route && this.$route.query ? this.$route.query : {})
    if (!this.news && options && Object.keys(options).length > 0) {
      // 目前支持直接通过 query 传递 title/url 等简要字段
      this.news = {
        title: options.title || '',
        url: options.url || options.newsUrl || '',
        image: options.image || '',
        date: options.date || ''
      }
    }
    // 如果有 html/content，进行清洗并准备渲染
    if (this.news && (this.news.html || this.news.content)) {
      this.news._safeHtml = this.sanitizeAndPrepareHtml(this.news.html || this.news.content)
    }

    // 如果没有 html/content，但有外部 url，尝试在 App 环境下拉取外部页面并清洗显示（避免 web-view 背景问题）
    if (this.news && !this.news._safeHtml && this.news.url) {
      // 在非H5环境（App）尝试请求外部 HTML
      // #ifndef H5
      this.tryFetchExternalHtml(this.news.url)
      // #endif
    }
  },
  methods: {
    goBack() {
      uni.navigateBack()
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      if (isNaN(date.getTime())) return dateStr
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },
    renderHtml() {
      if (!this.news) return ''
      return this.news._safeHtml || this.news.html || ''
    },
    // 安全处理content内容，保留正文图片，但移除危险属性
    sanitizeContent(content) {
      if (!content) return ''
      let cleanContent = String(content)
      // 移除所有事件处理器属性（如onclick/onerror等）
      cleanContent = cleanContent.replace(/\s+on[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, '')
      // 过滤style，仅移除背景相关与固定定位，保留其他样式
      cleanContent = cleanContent.replace(/\sstyle\s*=\s*("([^"]*)"|'([^']*)')/gi, (m, q, d1, d2) => {
        const css = (d1 || d2 || '')
        const filtered = css
          .split(';')
          .map(s => s.trim())
          .filter(Boolean)
          .filter(rule => {
            const key = rule.split(':')[0]?.trim().toLowerCase()
            if (!key) return false
            if (key.startsWith('background')) return false
            if (key === 'position') return false
            if (key === 'z-index') return false
            return true
          })
          .join('; ')
        return filtered ? ` style="${filtered}"` : ''
      })
      // 替换换行符为br标签
      return cleanContent.replace(/\n/g, '<br>')
    },
    // 打开外部链接（在浏览器中）
    openInBrowser() {
      if (!this.news || !this.news.url) return
      const url = this.news.url
      // H5
      // #ifdef H5
      window.open(url, '_blank')
      return
      // #endif

      // APP-PLUS
      // #ifdef APP-PLUS
      try {
        if (typeof plus !== 'undefined' && plus.runtime && plus.runtime.openURL) {
          plus.runtime.openURL(url)
          return
        }
      } catch (e) {
        console.warn('plus.runtime.openURL failed', e)
      }
      // 兜底复制
      // #endif
      uni.setClipboardData({
        data: url,
        success: () => {
          uni.showToast({ title: '链接已复制，请在浏览器中打开', icon: 'none' })
        }
      })
    },

    // 简单的 HTML 清洗与处理：移除 script/iframe 等危险标签，移除 on* 事件属性，允许的标签与属性白名单
    sanitizeAndPrepareHtml(rawHtml) {
      if (!rawHtml) return ''
      let html = String(rawHtml)

      // 移除 script/style/iframe/object/embed 等危险标签及其内容
      html = html.replace(/<\s*(script|style|iframe|object|embed|link)[^>]*>[\s\S]*?<\s*\/\s*\1\s*>/gi, '')

      // 移除事件处理器属性（onclick onerror 等）
      html = html.replace(/\s+on[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, '')

      // 移除所有内联 style 属性，避免外部内容通过 background-image 或大尺寸内联样式破坏布局
      html = html.replace(/\s+style\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, '')

      // 允许标签列表（保留常用文本标签与 img，以及常见分区容器）
      const allowedTags = ['p','br','strong','b','em','i','u','ul','ol','li','h1','h2','h3','h4','span','div','img','section','article','figure','figcaption']

      // 保留 img 标签，但清理其危险属性；支持懒加载字段 data-src/data-original 等
      html = html.replace(/<img([^>]*)>/gi, (m, attrs) => {
        function pick(name) {
          const m1 = attrs.match(new RegExp(`\\s${name}\\s*=\\s*(\"[^\"]*\"|'[^']*'|[^\\s>]+)`, 'i'))
          return m1 ? m1[1] || m1[0] : ''
        }
        // 依次取 src/data-src/data-original/data-url/data-actualsrc
        let srcVal = pick('src') || pick('data-src') || pick('data-original') || pick('data-url') || pick('data-actualsrc')
        srcVal = srcVal ? String(srcVal).replace(/^['\"]|['\"]$/g, '') : ''
        if (srcVal && srcVal.startsWith('//')) srcVal = 'https:' + srcVal
        const src = srcVal ? `src="${srcVal}"` : ''
        const alt = pick('alt') ? `alt=${pick('alt')}` : ''
        const title = pick('title') ? `title=${pick('title')}` : ''
        const width = pick('width') ? `width=${pick('width')}` : ''
        const height = pick('height') ? `height=${pick('height')}` : ''
        return `<img ${[src,alt,title,width,height].filter(Boolean).join(' ')}>`
      })

      // 链接标签替换为 span，避免点击跳走
      html = html.replace(/<a[^>]*>([\s\S]*?)<\/a>/gi, (match, text) => text || '')

      // 移除所有标签中不在白名单的标签（替换为其内部文本）
      html = html.replace(/<\/?([a-z0-9-]+)(\s[^>]*)?>/gi, (full, tagName) => {
        tagName = tagName.toLowerCase()
        if (allowedTags.includes(tagName)) {
          return full
        }
        return ''
      })

      return html
    }
    ,
    // APP内尝试抓取外部HTML并清洗，H5保留外链提示
    tryFetchExternalHtml(url) {
      if (!url) return
      this.loadingExternal = true
      this.externalFetchFailed = false
      // #ifdef APP-PLUS
      uni.request({
        url,
        method: 'GET',
        timeout: 8000,
        success: (res) => {
          const html = typeof res.data === 'string' ? res.data : ''
          if (html) {
            this.news._safeHtml = this.sanitizeAndPrepareHtml(html)
          } else {
            this.externalFetchFailed = true
          }
        },
        fail: () => {
          this.externalFetchFailed = true
        },
        complete: () => {
          this.loadingExternal = false
          if (this.externalFetchFailed && !this.news._safeHtml) {
            this.news._safeHtml = `<p>此新闻来自外部链接。</p><p>点击右上角\"在浏览器打开\"查看完整内容。</p>`
          }
        }
      })
      // #endif
      // #ifdef H5
      this.loadingExternal = false
      this.externalFetchFailed = true
      if (!this.news._safeHtml) {
        this.news._safeHtml = `<p>此新闻来自外部链接。</p><p>点击右上角\"在浏览器打开\"查看完整内容。</p>`
      }
      // #endif
    }
  }
}
</script>

<style scoped>
.news-detail-page {
  min-height: 100vh;
  background: var(--ds-bg);
  font-family: var(--ds-font);
}
.header {
  height: auto;
  padding: 52px 16px 12px;
  display: flex;
  align-items: center;
  background: rgba(244,246,251,0.85);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--ds-hairline);
  position: sticky;
  top: 0;
  z-index: 100;
}
.back {
  color: var(--ds-brand);
  font-weight: 600;
  margin-right: 12px;
  padding: 6px 10px;
  border-radius: 10px;
  background: var(--ds-brand-soft);
  font-size: 14px;
}
.title {
  font-size: 16px;
  font-weight: 700;
  color: var(--ds-ink-1);
  flex: 1;
  text-align: center;
  margin-right: 60px;
}
.open-btn {
  position: absolute;
  right: 16px;
  color: var(--ds-brand);
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--ds-r-pill);
  background: var(--ds-brand-soft);
  font-weight: 600;
}
.content {
  padding: 18px 20px 30px;
  background: var(--ds-bg);
}
.web-container {
  height: calc(100vh - 110px);
  background: var(--ds-surface);
  overflow: hidden;
}
.detail-webview {
  width: 100%;
  height: 100%;
  display: block;
}
.news-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--ds-ink-1);
  line-height: 1.4;
  margin-bottom: 10px;
}
.meta {
  display: flex;
  gap: 10px;
  color: var(--ds-ink-3);
  font-size: 12px;
  margin-bottom: 16px;
  font-family: var(--ds-font-mono);
  letter-spacing: 0.3px;
}
.news-body {
  font-size: 15px;
  color: var(--ds-ink-2);
  line-height: 1.75;
}
.news-body :deep(*) {
  background: transparent !important;
  background-image: none !important;
  background-repeat: no-repeat !important;
  background-size: auto !important;
  position: static !important;
}
.news-body :deep(img) { max-width: 100% !important; height: auto !important; display: inline-block !important; border-radius: var(--ds-r-sm); margin: 8px 0; }
.news-body :deep(a) { color: var(--ds-brand); text-decoration: none; }
.news-body :deep(p) { margin-bottom: 12px; }
.news-body :deep(h1), .news-body :deep(h2), .news-body :deep(h3) { color: var(--ds-ink-1); font-weight: 700; margin: 16px 0 10px; }

.no-content {
  color: var(--ds-ink-4);
  text-align: center;
  padding: 40px 20px;
}
.loading-placeholder {
  padding: 40px;
  text-align: center;
  color: var(--ds-ink-3);
  font-size: 13px;
}
</style>
