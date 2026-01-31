/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  corePlugins: {
    preflight: false
  },
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // 政务专属配色系统
        gov: {
          primary: '#0A2463',        // 藏青 - 政务专属主色
          'primary-dark': '#122349',  // 墨蓝 - 深色主色
          'primary-light': '#2C3E50', // 深炭灰 - 浅色主色
          secondary: '#34495E',       // 深炭灰变体
          accent: '#B8860B',          // 哑光金 - 点缀色
          'accent-light': '#D4B96A',  // 浅米金 - 浅色点缀
          background: '#F8F9FA',      // 浅米灰 - 页面底色
          'background-light': '#F5F5F5', // 极浅灰 - 卡片底色
          text: '#2C3E50',            // 深色文本
          'text-muted': '#6C757D',    // 次要文本
          border: '#E9ECEF',          // 边框色
          'border-light': '#F1F3F5',  // 浅边框
          'border-dark': '#DEE2E6',   // 深边框
          success: '#1E7E34',         // 成功绿 - 降低30%饱和度
          warning: '#B8860B',         // 提醒黄 - 使用哑光金
          error: '#A0281A',           // 警示红 - 降低30%饱和度
        }
      },
      fontFamily: {
        heading: ['Noto Sans SC', 'Microsoft YaHei', '微软雅黑', 'PingFang SC', 'Hiragino Sans GB', 'sans-serif'],
        body: ['Noto Sans SC', 'Microsoft YaHei', '微软雅黑', 'PingFang SC', 'Hiragino Sans GB', 'sans-serif'],
        title: ['Noto Sans SC', 'Microsoft YaHei', '微软雅黑', 'STSong', 'SimSun', 'serif'],
      },
      spacing: {
        'xs': '0.5rem',   // 8px
        'sm': '1rem',     // 16px
        'md': '1.5rem',   // 24px
        'lg': '2rem',     // 32px
        'xl': '3rem',     // 48px
        '2xl': '4rem',    // 64px
      },
      borderRadius: {
        'gov-sm': '0.25rem',   // 4px
        'gov-md': '0.375rem',  // 6px
        'gov-lg': '0.5rem',    // 8px
        'gov-xl': '0.75rem',   // 12px
      },
      boxShadow: {
        'gov-sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'gov-md': '0 2px 4px rgba(0, 0, 0, 0.05)',
        'gov-lg': '0 2px 4px rgba(0, 0, 0, 0.05)',
        'gov-xl': '0 4px 8px rgba(0, 0, 0, 0.08)',
        'gov-2xl': '0 8px 16px rgba(0, 0, 0, 0.1)',
      }
    }
  }
}

