import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 页面设置
st.set_page_config(
    page_title="社交媒体献血话题舆情可视化系统", 
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS美化
st.markdown("""
<style>
    .css-1d391kg { padding-top: 1rem; }
    .stButton button { border-radius: 20px; transition: all 0.3s ease; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    hr { margin: 1rem 0; border: none; height: 2px; background: linear-gradient(90deg, transparent, #ff4b4b, transparent); }
    h1, h2, h3 { font-weight: 600; }
    
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 1.2rem; color: white; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .metric-value { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
    .metric-label { font-size: 0.9rem; opacity: 0.9; }
    
    .wordcloud-container { background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; text-align: center; }
    
    .typical-card { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; border-left: 4px solid #ff4b4b; transition: all 0.3s ease; }
    .typical-card:hover { transform: translateX(5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .typical-positive { border-left-color: #28a745; }
    .typical-neutral { border-left-color: #ffc107; }
    .typical-negative { border-left-color: #dc3545; }
    
    .comment-text { font-size: 1rem; line-height: 1.5; color: #333; margin-bottom: 0.8rem; }
    .comment-meta { font-size: 0.8rem; color: #666; display: flex; gap: 1rem; flex-wrap: wrap; }
    .comment-topic { background: #e9ecef; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.75rem; }
    
    .page-transition { animation: fadeIn 0.5s ease-in; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    
    .filter-panel { background: #f8f9fa; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; }
    .warning-badge { background-color: #fff3cd; color: #856404; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


# ========== 加载数据 ==========
# 定义列名常量（根据实际数据集列名）
COL_CONTENT = '评论内容'
COL_PLATFORM = '平台'
COL_LIKES = '点赞数'
COL_REPLIES = '回复数'
COL_TIME = '评论时间'
COL_VIDEO_TITLE = '视频标题'
COL_VIDEO_TYPE = '视频类型'
COL_POST_CONTENT = '帖子内容'
COL_POST_CATEGORY = '帖子分类'
COL_TOPIC = '评论主题'
COL_SENTIMENT_SCORE = '情感得分'
COL_SENTIMENT = '情感倾向'


@st.cache_data
def load_analysis_data():
    """加载多平台分析数据集"""
    df = pd.read_excel('platform4_analyzed.xlsx')
    
    # 处理时间列
    if COL_TIME in df.columns:
        df[COL_TIME] = pd.to_datetime(df[COL_TIME])
        df['年月'] = df[COL_TIME].dt.strftime('%Y-%m')
    elif '时间' in df.columns:
        df['时间'] = pd.to_datetime(df['时间'])
        df['年月'] = df['时间'].dt.strftime('%Y-%m')
    
    # 确保平台列存在
    if COL_PLATFORM not in df.columns:
        st.warning("数据中未找到'平台'列，将默认所有数据来自B站")
        df[COL_PLATFORM] = 'B站'
    
    return df


@st.cache_data
def load_typical_comments():
    """加载典型评论数据"""
    try:
        df = pd.read_excel('sample_data.xlsx')
        return df
    except FileNotFoundError:
        return pd.DataFrame({
            COL_CONTENT: ['暂无典型评论数据，请确保sample_data.xlsx文件存在'],
            COL_SENTIMENT: ['中性'],
            COL_SENTIMENT_SCORE: [0.5],
            COL_LIKES: [0],
            COL_REPLIES: [0],
            COL_TOPIC: ['其他'],
            COL_PLATFORM: ['B站']
        })


# 加载数据
df = load_analysis_data()
df_typical = load_typical_comments()

# 平台列表
ALL_PLATFORMS = sorted(df[COL_PLATFORM].unique().tolist()) if COL_PLATFORM in df.columns else ['B站']


# ========== 页面导航 ==========
st.title("🩸 社交媒体献血话题舆情可视化系统")
st.markdown("基于B站、微博、知乎、抖音多平台献血相关评论的情感分析与主题挖掘 | 数据量：11214条")


col1, col2 = st.columns(2)
with col1:
    if st.button("📊 **分析成果概览**", use_container_width=True, type="primary"):
        st.session_state.page = "overview"
with col2:
    if st.button("🔍 **交互式数据探索**", use_container_width=True):
        st.session_state.page = "explore"

if 'page' not in st.session_state:
    st.session_state.page = "overview"

st.markdown("---")


# ==================== 页面1：分析成果概览 ====================
if st.session_state.page == "overview":
    st.markdown('<div class="page-transition">', unsafe_allow_html=True)
    
    # ---------- 数据概览指标 ----------
    st.subheader("📊 数据概览")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📝 总评论数</div>
            <div class="metric-value">{len(df):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_score = df[COL_SENTIMENT_SCORE].mean() if COL_SENTIMENT_SCORE in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💯 平均情感得分</div>
            <div class="metric-value">{avg_score:.3f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        platform_count = df[COL_PLATFORM].nunique() if COL_PLATFORM in df.columns else 1
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🌐 覆盖平台</div>
            <div class="metric-value">{platform_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        positive_ratio = (df[COL_SENTIMENT] == '正向').sum() / len(df) * 100 if COL_SENTIMENT in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">😊 正向评论占比</div>
            <div class="metric-value">{positive_ratio:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        negative_ratio = (df[COL_SENTIMENT] == '负向').sum() / len(df) * 100 if COL_SENTIMENT in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">😞 负向评论占比</div>
            <div class="metric-value">{negative_ratio:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ---------- 第一行：平台对比 ----------
    st.subheader("📊 多平台数据对比")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📈 各平台数据量分布")
        try:
            st.image('各平台数据量柱状图.png', use_container_width=True)
        except:
            st.info("各平台数据量柱状图加载失败")
    
    with col2:
        st.markdown("##### 📦 各平台情感得分对比")
        try:
            st.image('各平台情感得分箱线图.png', use_container_width=True)
        except:
            st.info("各平台情感得分箱线图加载失败")
    
    st.markdown("---")
    
    # ---------- 第二行：情感分布 ----------
    st.subheader("🎭 情感倾向分析")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🍩 全平台情感分布")
        try:
            st.image('全平台情感分布饼图.png', use_container_width=True)
        except:
            st.info("全平台情感分布饼图加载失败")
    
    with col2:
        st.markdown("##### 📊 各平台情感分布")
        try:
            st.image('各平台情感分布分组柱状图.png', use_container_width=True)
        except:
            st.info("各平台情感分布分组柱状图加载失败")
    
    st.markdown("---")
    
    # ---------- 第三行：主题分析 ----------
    st.subheader("🏷️ 主题分析")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🥧 全平台评论主题分布")
        try:
            st.image('全平台评论主题分布图.png', use_container_width=True)
        except:
            st.info("全平台评论主题分布图加载失败")
    
    with col2:
        st.markdown("##### 📊 全平台各主题情感得分")
        try:
            st.image('全平台各主题情感得分分布.png', use_container_width=True)
        except:
            st.info("全平台各主题情感得分分布加载失败")
    
    st.markdown("---")
    
    # ---------- 第四行：B站-微博对比 ----------
    st.subheader("📱 B站 vs 微博 内容对比分析")
    try:
        st.image('B站-微博 内容分布情感得分对比.png', use_container_width=True)
    except:
        st.info("B站-微博内容对比图加载失败")
    
    st.markdown("---")
    
    # ---------- 第五行：情感趋势 ----------
    st.subheader("📈 情感趋势分析")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 全平台情感趋势")
        try:
            st.image('全平台情感趋势图.png', use_container_width=True)
        except:
            st.info("全平台情感趋势图加载失败")
    
    with col2:
        st.markdown("##### 分平台情感趋势")
        try:
            st.image('分平台情感趋势图.png', use_container_width=True)
        except:
            st.info("分平台情感趋势图加载失败")
    
    st.markdown("---")
    
    # ---------- 第六行：词云 ----------
    st.subheader("☁️ 词云分析")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 整体词云")
        try:
            st.image('全平台词云图.png', use_container_width=True)
        except:
            st.info("整体词云加载失败")
    
    with col2:
        st.markdown("##### 正面评论词云")
        try:
            st.image('正向词云图.png', use_container_width=True)
        except:
            st.info("正面词云加载失败")
    
    with col3:
        st.markdown("##### 负面评论词云")
        try:
            st.image('负向词云图.png', use_container_width=True)
        except:
            st.info("负面词云加载失败")
    
    st.markdown("---")
    
    # ---------- 第七行：典型评论案例 ----------
    st.subheader("⭐ 典型评论案例")
    
    if COL_SENTIMENT in df_typical.columns:
        df_typical['border_class'] = df_typical[COL_SENTIMENT].map({
            '正向': 'typical-positive',
            '中性': 'typical-neutral',
            '负向': 'typical-negative'
        }).fillna('')
    
    for idx, row in df_typical.head(6).iterrows():
        border_class = row.get('border_class', '')
        sentiment = row.get(COL_SENTIMENT, '')
        sentiment_emoji = '😊' if sentiment == '正向' else ('😐' if sentiment == '中性' else '😞')
        
        st.markdown(f"""
        <div class="typical-card {border_class}">
            <div class="comment-text">{row[COL_CONTENT]}</div>
            <div class="comment-meta">
                <span>{sentiment_emoji} 情感倾向: {sentiment}</span>
                <span>📊 情感得分: {row.get(COL_SENTIMENT_SCORE, 'N/A')}</span>
                <span>❤️ 点赞: {row.get(COL_LIKES, 'N/A')}</span>
                <span>💬 回复: {row.get(COL_REPLIES, 'N/A')}</span>
                <span class="comment-topic">🏷️ 主题: {row.get(COL_TOPIC, 'N/A')}</span>
                <span>📱 平台: {row.get(COL_PLATFORM, 'N/A')}</span>
                <span>📅 时间: {row.get(COL_TIME, 'N/A')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==================== 页面2：交互式数据探索 ====================
else:
    st.markdown('<div class="page-transition">', unsafe_allow_html=True)
    
    st.subheader("🔍 交互式数据探索")
    st.markdown("通过侧边栏筛选条件，动态查看不同维度的分析结果")
    
    # ---------- 侧边栏筛选器 ----------
    with st.sidebar:
        st.markdown("## 🎛️ 筛选控制面板")
        st.markdown("---")
        
        st.markdown("##### 📊 数据概览")
        st.info(f"总评论数: **{len(df):,}** 条 | 覆盖平台: **{df[COL_PLATFORM].nunique()}** 个")
        st.markdown("---")
        
        # ===== 平台筛选 =====
        if COL_PLATFORM in df.columns:
            st.markdown("##### 📱 平台筛选")
            
            if "platform_select" not in st.session_state:
                st.session_state.platform_select = ALL_PLATFORMS.copy()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 全选平台", key="select_all_platform", use_container_width=True):
                    st.session_state.platform_select = ALL_PLATFORMS.copy()
            with col2:
                if st.button("❌ 清空平台", key="clear_all_platform", use_container_width=True):
                    st.session_state.platform_select = []
                    st.rerun()
            
            st.multiselect(
                "选择平台（支持多选）",
                options=ALL_PLATFORMS,
                key="platform_select"
            )
            st.markdown("---")
        
        # ===== 情感倾向筛选 =====
        if COL_SENTIMENT in df.columns:
            st.markdown("##### 📌 情感倾向")
            sentiment_options = list(df[COL_SENTIMENT].unique())
            
            if "sentiment_select" not in st.session_state:
                st.session_state.sentiment_select = sentiment_options.copy()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 全选情感", key="select_all", use_container_width=True):
                    st.session_state.sentiment_select = sentiment_options.copy()
            with col2:
                if st.button("❌ 清空情感", key="clear_all", use_container_width=True):
                    st.session_state.sentiment_select = []
                    st.rerun()
            
            st.multiselect(
                "选择情感类型",
                options=sentiment_options,
                key="sentiment_select"
            )
            st.markdown("---")
        
        # ===== 主题筛选 =====
        if COL_TOPIC in df.columns:
            st.markdown("##### 🏷️ 评论主题")
            topic_options = list(df[COL_TOPIC].unique())
            
            if "topic_select" not in st.session_state:
                st.session_state.topic_select = topic_options.copy()
            
            st.multiselect(
                "选择主题类型",
                options=topic_options,
                key="topic_select"
            )
            st.markdown("---")
        
        # ===== 情感得分范围筛选 =====
        if COL_SENTIMENT_SCORE in df.columns:
            st.markdown("##### 📊 情感得分范围")
            if "score_range" not in st.session_state:
                st.session_state.score_range = (0.0, 1.0)
            
            st.slider(
                "选择得分范围",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.score_range,
                step=0.05,
                key="score_range",
                format="%.2f"
            )
            st.markdown("---")
        
        # ===== 点赞数筛选 =====
        if COL_LIKES in df.columns:
            st.markdown("##### ❤️ 最低点赞数")
            min_likes = int(df[COL_LIKES].min())
            max_likes = int(df[COL_LIKES].max())
            
            if "likes_threshold" not in st.session_state:
                st.session_state.likes_threshold = min_likes
            
            st.slider(
                "选择最低点赞数",
                min_value=min_likes,
                max_value=max_likes,
                value=st.session_state.likes_threshold,
                step=10,
                key="likes_threshold"
            )
            st.markdown("---")
        
        # ===== 时间范围筛选 =====
        if '年月' in df.columns:
            st.markdown("##### 📅 时间范围")
            all_months = sorted(df['年月'].unique())
            
            if "start_month" not in st.session_state:
                st.session_state.start_month = all_months[0] if all_months else ''
            if "end_month" not in st.session_state:
                st.session_state.end_month = all_months[-1] if all_months else ''
            
            if all_months:
                col1, col2 = st.columns(2)
                with col1:
                    st.selectbox("开始", options=all_months, key="start_month")
                with col2:
                    st.selectbox("结束", options=all_months, key="end_month")
            st.markdown("---")
        
        # ===== 重置按钮 =====
        if st.button("🔄 重置所有筛选", key="reset_all", use_container_width=True):
            keys_to_delete = ["platform_select", "sentiment_select", "topic_select", 
                            "score_range", "likes_threshold", "start_month", "end_month"]
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.caption("💡 提示：右侧图表将根据筛选条件实时更新")
    
    # ---------- 应用筛选条件 ----------
    filtered_df = df.copy()
    
    # 平台筛选
    if "platform_select" in st.session_state and st.session_state.platform_select:
        filtered_df = filtered_df[filtered_df[COL_PLATFORM].isin(st.session_state.platform_select)]
    
    # 情感倾向筛选
    if "sentiment_select" in st.session_state and st.session_state.sentiment_select:
        filtered_df = filtered_df[filtered_df[COL_SENTIMENT].isin(st.session_state.sentiment_select)]
    
    # 主题筛选
    if "topic_select" in st.session_state and st.session_state.topic_select:
        filtered_df = filtered_df[filtered_df[COL_TOPIC].isin(st.session_state.topic_select)]
    
    # 情感得分筛选
    if "score_range" in st.session_state:
        filtered_df = filtered_df[
            (filtered_df[COL_SENTIMENT_SCORE] >= st.session_state.score_range[0]) & 
            (filtered_df[COL_SENTIMENT_SCORE] <= st.session_state.score_range[1])
        ]
    
    # 点赞数筛选
    if "likes_threshold" in st.session_state:
        filtered_df = filtered_df[filtered_df[COL_LIKES] >= st.session_state.likes_threshold]
    
    # 时间范围筛选
    if "start_month" in st.session_state and "end_month" in st.session_state:
        filtered_df = filtered_df[
            (filtered_df['年月'] >= st.session_state.start_month) & 
            (filtered_df['年月'] <= st.session_state.end_month)
        ]
    
    # ---------- 主界面 ----------
    st.success(f"📊 当前筛选结果：共 **{len(filtered_df)}** 条评论（原始数据 **{len(df):,}** 条）")
    
    # 当前筛选平台分布
    if COL_PLATFORM in filtered_df.columns and len(filtered_df) > 0:
        st.subheader("📁 当前筛选平台分布")
        platform_counts = filtered_df[COL_PLATFORM].value_counts().reset_index()
        platform_counts.columns = ['平台', '数量']
    
        # 指定平台显示顺序
        platform_order = ['B站', '微博', '知乎', '抖音']
        platform_order = [p for p in platform_order if p in platform_counts['平台'].values]
    
        # 按顺序重新排列
        platform_counts['平台'] = pd.Categorical(platform_counts['平台'], categories=platform_order, ordered=True)
        platform_counts = platform_counts.sort_values('平台').reset_index(drop=True)
    
        # 定义颜色列表（按顺序对应）
        color_map = {
            'B站': '#FF6B6B',
            '微博': '#4ECDC4',
            '知乎': '#45B7D1',
            '抖音': '#FECA57'
        }
        # 按平台顺序生成颜色列表
        colors = [color_map[p] for p in platform_counts['平台']]
    
        # 创建图形
        fig = go.Figure()
    
        # 添加柱状图
        fig.add_trace(go.Bar(
            x=platform_counts['平台'],
            y=platform_counts['数量'],
            text=platform_counts['数量'],
            textposition='outside',
            marker_color=colors,  # 直接传颜色列表，不是字典
            textfont=dict(size=12),
            width=0.6
        ))
    
        fig.update_layout(
            title='平台数据量分布',
            xaxis_title='平台',
            yaxis_title='评论数量（条）',
            xaxis={
                'type': 'category',
                'categoryorder': 'array',
                'categoryarray': platform_order,
                'tickangle': 0,
                'side': 'bottom'
            },
            showlegend=False
        )
    
        st.plotly_chart(fig, use_container_width=True)
    
    # 指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 评论总数", len(filtered_df))
    with col2:
        avg_score = filtered_df[COL_SENTIMENT_SCORE].mean() if len(filtered_df) > 0 else 0
        st.metric("💯 平均情感得分", f"{avg_score:.3f}")
    with col3:
        pos_count = (filtered_df[COL_SENTIMENT] == '正向').sum() if len(filtered_df) > 0 else 0
        st.metric("😊 正向评论", pos_count)
    with col4:
        neg_count = (filtered_df[COL_SENTIMENT] == '负向').sum() if len(filtered_df) > 0 else 0
        st.metric("😞 负向评论", neg_count)
    
    st.markdown("---")
    
    # 情感分布
    col1, col2 = st.columns(2)
    with col1:
        if len(filtered_df) > 0 and COL_SENTIMENT in filtered_df.columns:
            sentiment_counts = filtered_df[COL_SENTIMENT].value_counts().reset_index()
            sentiment_counts.columns = [COL_SENTIMENT, '数量']
            fig_pie = px.pie(sentiment_counts, values='数量', names=COL_SENTIMENT,
                             title=f'情感分布 ({len(filtered_df)}条)', hole=0.3,
                             color=COL_SENTIMENT,
                             color_discrete_map={'正向': '#28a745', '中性': '#ffc107', '负向': '#dc3545'})
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        if len(filtered_df) > 0 and COL_SENTIMENT_SCORE in filtered_df.columns:
            fig_hist = px.histogram(filtered_df, x=COL_SENTIMENT_SCORE, nbins=20,
                                     title='情感得分分布', color_discrete_sequence=['#17a2b8'])
            fig_hist.add_vline(x=avg_score, line_dash="dash", line_color="red",
                               annotation_text=f"均值: {avg_score:.3f}")
            st.plotly_chart(fig_hist, use_container_width=True)
    
    # 平台情感对比（动态箱线图）
    if len(filtered_df) > 0 and COL_PLATFORM in filtered_df.columns and len(filtered_df[COL_PLATFORM].unique()) > 1:
        st.subheader("📊 各平台情感得分对比")
        fig_box = px.box(filtered_df, x=COL_PLATFORM, y=COL_SENTIMENT_SCORE, 
                         title='平台情感得分分布', color=COL_PLATFORM, points='outliers')
        fig_box.add_hline(y=0.5, line_dash='dash', line_color='gray', annotation_text='中性线 (0.5)')
        st.plotly_chart(fig_box, use_container_width=True)
    
    # 主题情感分析
    if len(filtered_df) > 0 and COL_TOPIC in filtered_df.columns:
        st.subheader("🏷️ 各主题情感分析")
        topic_stats = filtered_df.groupby(COL_TOPIC).agg({
            COL_SENTIMENT_SCORE: 'mean',
            COL_CONTENT: 'count'
        }).reset_index().rename(columns={COL_SENTIMENT_SCORE: '平均情感得分', COL_CONTENT: '评论数量'})
        topic_stats = topic_stats.sort_values('平均情感得分', ascending=False)
        
        fig_topic = px.bar(topic_stats, x=COL_TOPIC, y='平均情感得分',
                           color='平均情感得分', text='评论数量',
                           title='各主题平均情感得分',
                           color_continuous_scale='RdYlGn')
        fig_topic.update_traces(textposition='outside')
        st.plotly_chart(fig_topic, use_container_width=True)
    
    # 时间趋势
    if len(filtered_df) > 0 and '年月' in filtered_df.columns:
        st.subheader("📅 时间趋势分析")
        monthly = filtered_df.groupby('年月').agg({
            COL_SENTIMENT_SCORE: 'mean',
            COL_CONTENT: 'count'
        }).reset_index().rename(columns={COL_SENTIMENT_SCORE: '平均情感得分', COL_CONTENT: '评论数量'})
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly['年月'], y=monthly['平均情感得分'],
                                  mode='lines+markers', name='平均情感得分',
                                  line=dict(color='#ff4b4b', width=3), yaxis='y1'))
        fig.add_trace(go.Bar(x=monthly['年月'], y=monthly['评论数量'],
                              name='评论数量', marker_color='rgba(23,162,184,0.5)', yaxis='y2'))
        fig.update_layout(title='情感得分与评论数量月度变化',
                          yaxis=dict(title='平均情感得分', range=[0, 1]),
                          yaxis2=dict(title='评论数量', overlaying='y', side='right'))
        st.plotly_chart(fig, use_container_width=True)
    
    # 评论详情表格
    st.subheader("📝 评论详情")
    display_cols = [c for c in [COL_CONTENT, COL_PLATFORM, COL_SENTIMENT_SCORE, COL_SENTIMENT, 
                                 COL_TOPIC, COL_LIKES, '年月'] if c in filtered_df.columns]
    
    if len(filtered_df) > 0:
        st.dataframe(filtered_df[display_cols].head(100), use_container_width=True, height=400)
        csv = filtered_df[display_cols].to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下载筛选结果 (CSV)", data=csv, file_name='filtered_comments.csv', mime='text/csv')
    else:
        st.info("当前筛选条件下没有数据")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ========== 页脚 ==========
st.markdown("---")
st.caption("Made with ❤️ 热血心声 | 基于多平台献血评论情感分析 | 数据量：11214条评论 | 支持平台：B站、微博、知乎、抖音")


# ========== 使用说明 ==========
if st.session_state.page == "overview":
    with st.expander("📖 使用说明"):
        st.markdown("""
        ### 🎯 功能介绍
        
        **📊 分析成果概览**
        - 展示完整的分析成果，包括多平台对比、主题分布、情感趋势、词云图等
        - 支持B站、微博、知乎、抖音四平台数据对比
        - 包含典型评论案例，直观了解各类评论特征
        
        **🔍 交互式数据探索**
        - 通过左侧筛选器进行多维度数据筛选
        - **新增平台筛选**：支持B站/微博/知乎/抖音多选
        - 图表实时更新，支持情感倾向、主题、情感得分、点赞数、时间范围等筛选
        - 支持数据排序和下载
        
        ### 📊 数据说明
        - 数据来源：B站、微博、知乎、抖音献血相关评论
        - 分析样本：11214条评论（B站1494 + 微博7308 + 知乎1768 + 抖音644）
        - 情感分析：调用大模型API进行情感得分计算（0-1分）
        - 主题分类：调用大模型API进行评论主题分类
        
        ### 💡 使用建议
        - 点击顶部按钮切换页面
        - 在探索页面可以组合多个筛选条件进行交叉分析
        - 抖音数据量相对较少（644条），分析时请注意样本代表性
        """)