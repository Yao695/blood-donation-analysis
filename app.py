import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 页面设置
st.set_page_config(
    page_title="B站献血评论情感分析系统", 
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS美化
st.markdown("""
<style>
    /* 侧边栏样式 */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* 按钮样式 */
    .stButton button {
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* 分隔线样式 */
    hr {
        margin: 1rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ff4b4b, transparent);
    }
    
    /* 标题样式 */
    h1, h2, h3 {
        font-weight: 600;
    }
    
    /* 导航标签样式 */
    .nav-tabs {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    
    .nav-tab {
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 500;
        cursor: pointer;
        border-radius: 10px 10px 0 0;
        transition: all 0.3s ease;
        background: transparent;
        color: #666;
    }
    
    .nav-tab:hover {
        background: #f5f5f5;
        color: #ff4b4b;
    }
    
    .nav-tab-active {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%);
        color: white;
    }
    
    /* 指标卡片样式 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* 词云图容器样式 */
    .wordcloud-container {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* 典型评论卡片样式 */
    .typical-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #ff4b4b;
        transition: all 0.3s ease;
    }
    
    .typical-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .typical-positive {
        border-left-color: #28a745;
    }
    
    .typical-neutral {
        border-left-color: #ffc107;
    }
    
    .typical-negative {
        border-left-color: #dc3545;
    }
    
    .comment-text {
        font-size: 1rem;
        line-height: 1.5;
        color: #333;
        margin-bottom: 0.8rem;
    }
    
    .comment-meta {
        font-size: 0.8rem;
        color: #666;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .comment-topic {
        background: #e9ecef;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
    }
    
    /* 页面切换动画 */
    .page-transition {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 筛选器面板样式 */
    .filter-panel {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== 加载数据 ==========
@st.cache_data
def load_analysis_data():
    """加载分析数据集"""
    df = pd.read_excel('df_with_topic.xlsx')
    
    # 处理时间列（如果有）
    if '评论时间' in df.columns:
        df['评论时间'] = pd.to_datetime(df['评论时间'])
        df['年月'] = df['评论时间'].dt.strftime('%Y-%m')
    elif '时间' in df.columns:
        df['时间'] = pd.to_datetime(df['时间'])
        df['年月'] = df['时间'].dt.strftime('%Y-%m')
    
    return df

@st.cache_data
def load_typical_comments():
    """加载典型评论数据（用于展示）"""
    df = pd.read_excel('typical_comments.xlsx')
    return df

# 加载数据
df = load_analysis_data()
df_typical = load_typical_comments()

# ========== 页面导航 ==========
st.title("🩸 B站献血评论情感分析系统")
st.markdown("基于B站献血相关视频评论的情感分析与主题挖掘")

# 创建两个页面选项
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 **分析成果概览**", use_container_width=True, type="primary"):
        st.session_state.page = "overview"
        
with col2:
    if st.button("🔍 **交互式数据探索**", use_container_width=True):
        st.session_state.page = "explore"

# 初始化页面状态
if 'page' not in st.session_state:
    st.session_state.page = "overview"

st.markdown("---")

# ========== 页面1：分析成果概览 ==========
if st.session_state.page == "overview":
    st.markdown('<div class="page-transition">', unsafe_allow_html=True)
    
    # 数据概览指标
    st.subheader("📊 数据概览")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📝 总评论数</div>
            <div class="metric-value">{len(df)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_score = df['情感得分'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💯 平均情感得分</div>
            <div class="metric-value">{avg_score:.3f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        positive_ratio = (df['情感倾向'] == '正向').sum() / len(df) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">😊 正向评论占比</div>
            <div class="metric-value">{positive_ratio:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        negative_ratio = (df['情感倾向'] == '负向').sum() / len(df) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">😞 负向评论占比</div>
            <div class="metric-value">{negative_ratio:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 预先生成的图表展示
    st.subheader("📊 核心分析成果")
    
    # 第一行：主题分布和情感得分分布
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("##### 🥧 评论主题分布")
        try:
            st.image('评论主题分布.png', use_container_width=True)
        except Exception as e:
            st.info("主题分布图加载失败")
    
    with col_right:
        st.markdown("##### 📊 各主题情感得分分布")
        try:
            st.image('各主题情感得分分布.png', use_container_width=True)
        except Exception as e:
            st.info("主题情感得分图加载失败")
    
    st.markdown("---")
    
    # 第二行：情感趋势图
    st.subheader("📈 情感趋势与评论量月度变化")
    try:
        st.image('情感趋势与评论量月度变化.png', use_container_width=True)
    except Exception as e:
        st.info("情感趋势图加载失败")
    
    st.markdown("---")
    
    # 第三行：词云图展示（三列）
    st.subheader("☁️ 词云分析")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 整体词云")
        try:
            st.image('献血评论-整体词云图.png', use_container_width=True)
        except Exception as e:
            st.info("整体词云加载失败")
    
    with col2:
        st.markdown("##### 正面评论词云")
        try:
            st.image('献血评论-正面情感词云图.png', use_container_width=True)
        except Exception as e:
            st.info("正面词云加载失败")
    
    with col3:
        st.markdown("##### 负面评论词云")
        try:
            st.image('献血评论-负面情感词云图.png', use_container_width=True)
        except Exception as e:
            st.info("负面词云加载失败")
    
    st.markdown("---")
    
    # 典型评论展示
    st.subheader("⭐ 典型评论案例")
    
    # 为典型评论添加标签
    if '情感倾向' in df_typical.columns:
        df_typical['border_class'] = df_typical['情感倾向'].map({
            '正向': 'typical-positive',
            '中性': 'typical-neutral', 
            '负向': 'typical-negative'
        }).fillna('')
    
    # 展示典型评论
    for idx, row in df_typical.iterrows():
        border_class = row.get('border_class', '')
        sentiment = row.get('情感倾向', '')
        sentiment_emoji = '😊' if sentiment == '正向' else ('😐' if sentiment == '中性' else '😞')
        
        st.markdown(f"""
        <div class="typical-card {border_class}">
            <div class="comment-text">{row['评论内容']}</div>
            <div class="comment-meta">
                <span>{sentiment_emoji} 情感倾向: {sentiment}</span>
                <span>📊 情感得分: {row.get('情感得分', 'N/A')}</span>
                <span>❤️ 点赞: {row.get('点赞数', 'N/A')}</span>
                <span>💬 回复: {row.get('回复数', 'N/A')}</span>
                <span class="comment-topic">🏷️ 主题: {row.get('api_topic', 'N/A')}</span>
                <span>🎬 类型: {row.get('视频类型', 'N/A')}</span>
                <span>📅 时间: {row.get('评论时间', 'N/A')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 页面2：交互式数据探索 ==========
else:
    st.markdown('<div class="page-transition">', unsafe_allow_html=True)
    
    st.subheader("🔍 交互式数据探索")
    st.markdown("通过侧边栏筛选条件，动态查看不同维度的分析结果")
    
    # ========== 侧边栏筛选器 ==========
    with st.sidebar:
        st.markdown("## 🎛️ 筛选控制面板")
        st.markdown("通过以下条件筛选数据，右侧图表将实时更新")
    
        st.markdown("---")
    
        # 数据统计概览
        st.markdown("##### 📊 数据概览")
        st.info(f"总评论数: **{len(df)}** 条")
    
        st.markdown("---")
    
        # ===== 情感倾向筛选 =====
        if '情感倾向' in df.columns:
            st.markdown("##### 📌 情感倾向")
            sentiment_options = list(df['情感倾向'].unique())

            # 初始化 session_state 中的 key（如果不存在）
            if "sentiment_select" not in st.session_state:
                st.session_state.sentiment_select = sentiment_options.copy()

            # 全选/取消全选按钮
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 全选", key="select_all", use_container_width=True):
                    st.session_state.sentiment_select = sentiment_options.copy()
                
            with col2:
                if st.button("❌ 清空", key="clear_all", use_container_width=True):
                    st.session_state.sentiment_select = []
                    st.rerun()

            # 修复：去掉 default 参数，只保留 key
            st.multiselect(
                "选择情感类型",
                options=sentiment_options,
                key="sentiment_select"  # 只使用 key，不要用 default
            )
    
        # ===== 主题筛选 =====
        if 'api_topic' in df.columns:
            st.markdown("##### 🏷️ 评论主题")
            topic_options = list(df['api_topic'].unique())
        
            if "topic_select" not in st.session_state:
                st.session_state.topic_select = topic_options.copy()
        
        
            st.multiselect(
                "选择主题类型",
                options=topic_options,
                key="topic_select"
            )
    
        # ===== 视频类型筛选 =====
        if '视频类型' in df.columns:
            st.markdown("##### 🎬 视频类型")
            video_types = ['全部'] + list(df['视频类型'].unique())
        
            if "video_type_select" not in st.session_state:
                st.session_state.video_type_select = '全部'
        
            st.selectbox(
                "选择视频类型",
                options=video_types,
                key="video_type_select"
            )
    
        # ===== 情感得分范围筛选 =====
        if '情感得分' in df.columns:
            st.markdown("##### 📊 情感得分范围")
            min_score = float(df['情感得分'].min())
            max_score = float(df['情感得分'].max())
        
            if "score_range" not in st.session_state:
                st.session_state.score_range = (min_score, max_score)
        
            st.slider(
                "选择得分范围",
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                key="score_range",
                format="%.2f"
            )
    
        # ===== 点赞数筛选 =====
        if '点赞数' in df.columns:
            st.markdown("##### ❤️ 最低点赞数")
            min_likes = int(df['点赞数'].min())
            max_likes = int(df['点赞数'].max())
        
            if "likes_threshold" not in st.session_state:
                st.session_state.likes_threshold = min_likes
        
            st.slider(
                "选择最低点赞数",
                min_value=min_likes,
                max_value=max_likes,
                step=10,
                key="likes_threshold"
            )
    
        # ===== 时间范围筛选 =====
        if '年月' in df.columns:
            st.markdown("##### 📅 时间范围")
            all_months = sorted(df['年月'].unique())
        
            if "start_month" not in st.session_state:
                st.session_state.start_month = all_months[0]
            if "end_month" not in st.session_state:
                st.session_state.end_month = all_months[-1]
        
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox(
                    "开始",
                    options=all_months,
                    key="start_month"
                )
            with col2:
                st.selectbox(
                    "结束",
                    options=all_months,
                    key="end_month"
                )
    
        st.markdown("---")
    
        # ===== 重置按钮 =====
        if st.button("🔄 重置所有筛选", key="reset_all", use_container_width=True):
            keys_to_delete = []
    
            if '情感倾向' in df.columns:
                keys_to_delete.append("sentiment_select")
            if 'api_topic' in df.columns:
                keys_to_delete.append("topic_select")
            if '视频类型' in df.columns:
                keys_to_delete.append("video_type_select")
            if '情感得分' in df.columns:
                keys_to_delete.append("score_range")
            if '点赞数' in df.columns:
                keys_to_delete.append("likes_threshold")
            if '年月' in df.columns:
                keys_to_delete.append("start_month")
                keys_to_delete.append("end_month")
            
            # 删除这些 key
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
           
    
        st.markdown("---")
        st.caption("💡 提示：右侧图表将根据筛选条件实时更新")
    
    # 应用筛选条件
    filtered_df = df.copy()

    # 情感倾向筛选
    if "sentiment_select" in st.session_state and st.session_state.sentiment_select:
        filtered_df = filtered_df[filtered_df['情感倾向'].isin(st.session_state.sentiment_select)]

    # 主题筛选
    if "topic_select" in st.session_state and st.session_state.topic_select:
        filtered_df = filtered_df[filtered_df['api_topic'].isin(st.session_state.topic_select)]

    # 视频类型筛选
    if "video_type_select" in st.session_state and st.session_state.video_type_select != '全部':
        filtered_df = filtered_df[filtered_df['视频类型'] == st.session_state.video_type_select]

    # 情感得分筛选
    if "score_range" in st.session_state:
        filtered_df = filtered_df[
            (filtered_df['情感得分'] >= st.session_state.score_range[0]) & 
            (filtered_df['情感得分'] <= st.session_state.score_range[1])
        ]

    # 点赞数筛选
    if "likes_threshold" in st.session_state:
        filtered_df = filtered_df[filtered_df['点赞数'] >= st.session_state.likes_threshold]

    # 时间范围筛选
    if "start_month" in st.session_state and "end_month" in st.session_state:
        filtered_df = filtered_df[
            (filtered_df['年月'] >= st.session_state.start_month) & 
            (filtered_df['年月'] <= st.session_state.end_month)
    ]
    
    # ========== 主界面：动态图表 ==========
    
    # 显示筛选统计
    st.success(f"📊 当前筛选结果：共 **{len(filtered_df)}** 条评论（原始数据 **{len(df)}** 条）")
    
    # 指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 评论总数",
            value=len(filtered_df),
            delta=f"{(len(filtered_df)/len(df)*100):.1f}%" if len(filtered_df) != len(df) else None
        )
    
    with col2:
        if '情感得分' in filtered_df.columns and len(filtered_df) > 0:
            avg_score = filtered_df['情感得分'].mean()
            st.metric(
                label="💯 平均情感得分",
                value=f"{avg_score:.3f}",
                delta="正面倾向" if avg_score > 0.6 else ("中性" if avg_score > 0.4 else "负面倾向")
            )
        else:
            st.metric(label="💯 平均情感得分", value="N/A")
    
    with col3:
        if '情感倾向' in filtered_df.columns and len(filtered_df) > 0:
            positive_count = (filtered_df['情感倾向'] == '正向').sum()
            positive_ratio = (positive_count / len(filtered_df)) * 100
            st.metric(
                label="😊 正向评论",
                value=f"{positive_count}",
                delta=f"{positive_ratio:.1f}%"
            )
        else:
            st.metric(label="😊 正向评论", value="N/A")
    
    with col4:
        if '情感倾向' in filtered_df.columns and len(filtered_df) > 0:
            negative_count = (filtered_df['情感倾向'] == '负向').sum()
            negative_ratio = (negative_count / len(filtered_df)) * 100
            st.metric(
                label="😞 负向评论",
                value=f"{negative_count}",
                delta=f"{negative_ratio:.1f}%"
            )
        else:
            st.metric(label="😞 负向评论", value="N/A")
    
    st.markdown("---")
    
    # 情感分布饼图
    col1, col2 = st.columns(2)
    
    with col1:
        if '情感倾向' in filtered_df.columns and len(filtered_df) > 0:
            sentiment_counts = filtered_df['情感倾向'].value_counts().reset_index()
            sentiment_counts.columns = ['情感倾向', '数量']
            
            fig_pie = px.pie(
                sentiment_counts, 
                values='数量', 
                names='情感倾向',
                title=f'情感分布 (当前筛选: {len(filtered_df)}条)',
                color='情感倾向',
                color_discrete_map={
                    '正向': '#28a745',
                    '中性': '#ffc107',
                    '负向': '#dc3545'
                },
                hole=0.3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("暂无数据")
    
    with col2:
        if '情感得分' in filtered_df.columns and len(filtered_df) > 0:
            fig_hist = px.histogram(
                filtered_df, 
                x='情感得分', 
                nbins=20,
                title='情感得分分布',
                color_discrete_sequence=['#17a2b8'],
                labels={'情感得分': '情感得分', 'count': '评论数量'}
            )
            avg_score = filtered_df['情感得分'].mean()
            fig_hist.add_vline(
                x=avg_score, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"均值: {avg_score:.3f}"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("暂无数据")
    
    # 主题情感分析
    if 'api_topic' in filtered_df.columns and '情感得分' in filtered_df.columns and len(filtered_df) > 0:
        st.subheader("🏷️ 各主题情感分析")
        
        topic_stats = filtered_df.groupby('api_topic').agg({
            '情感得分': ['mean', 'count'],
            '情感倾向': lambda x: (x == '正向').mean() * 100
        }).round(3)
        
        topic_stats.columns = ['平均情感得分', '评论数量', '正向比例(%)']
        topic_stats = topic_stats.reset_index()
        topic_stats = topic_stats.sort_values('平均情感得分', ascending=False)
        
        # 柱状图
        fig_topic = px.bar(
            topic_stats, 
            x='api_topic', 
            y='平均情感得分',
            color='平均情感得分',
            text='评论数量',
            title='各主题平均情感得分对比',
            color_continuous_scale='RdYlGn',
            labels={'api_topic': '主题', '平均情感得分': '平均情感得分'}
        )
        fig_topic.update_traces(textposition='outside')
        st.plotly_chart(fig_topic, use_container_width=True)
        
        # 数据表格
        with st.expander("📋 查看详细主题统计数据"):
            st.dataframe(topic_stats, use_container_width=True)
    
    # 时间趋势分析
    if '年月' in filtered_df.columns and len(filtered_df) > 0:
        st.subheader("📅 时间趋势分析")
        
        # 按月统计
        monthly_data = filtered_df.groupby('年月').agg({
            '情感得分': 'mean',
            '评论内容': 'count'
        }).reset_index()
        monthly_data.columns = ['年月', '平均情感得分', '评论数量']
        
        # 双轴图
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_data['年月'],
            y=monthly_data['平均情感得分'],
            mode='lines+markers',
            name='平均情感得分',
            line=dict(color='#ff4b4b', width=3),
            marker=dict(size=8),
            yaxis='y1'
        ))
        
        fig.add_trace(go.Bar(
            x=monthly_data['年月'],
            y=monthly_data['评论数量'],
            name='评论数量',
            marker_color='rgba(23, 162, 184, 0.5)',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='情感得分与评论数量月度变化',
            xaxis_title='时间',
            yaxis=dict(title='平均情感得分', range=[0, 1], side='left'),
            yaxis2=dict(title='评论数量', overlaying='y', side='right'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 评论详情表格
    st.subheader("📝 评论详情")
    
    display_cols = []
    for col in ['评论内容', '情感得分', '情感倾向', 'api_topic', '点赞数', '视频类型', '年月']:
        if col in filtered_df.columns:
            display_cols.append(col)
    
    if len(filtered_df) > 0:
        # 排序选项
        sort_cols = [col for col in display_cols if col != '评论内容']
        if sort_cols:
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox("按列排序", options=sort_cols, key="sort_col")
            with col2:
                sort_order = st.radio("排序方式", options=["降序", "升序"], horizontal=True, key="sort_order")
            ascending = (sort_order == "升序")
            sorted_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
        else:
            sorted_df = filtered_df
        
        st.dataframe(
            sorted_df[display_cols].head(100),
            use_container_width=True,
            height=400
        )
        
        # 下载按钮
        csv = sorted_df[display_cols].to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载筛选结果 (CSV)",
            data=csv,
            file_name='filtered_comments.csv',
            mime='text/csv'
        )
    else:
        st.info("当前筛选条件下没有数据")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.caption("Made with ❤️ 三人小队 | 基于B站献血评论情感分析 | 数据量：1500+条评论")

# 使用说明（仅在概览页面显示）
if st.session_state.page == "overview":
    with st.expander("📖 使用说明"):
        st.markdown("""
        ### 🎯 功能介绍
        
        **📊 分析成果概览**
        - 展示完整的分析成果，包括主题分布、情感趋势、词云图等
        - 包含典型评论案例，直观了解各类评论特征
        
        **🔍 交互式数据探索**
        - 通过左侧筛选器进行多维度数据筛选
        - 图表实时更新，支持情感倾向、主题、视频类型、情感得分、点赞数、时间范围等筛选
        - 支持数据排序和下载
        
        ### 📊 数据说明
        - 数据来源：B站献血相关视频评论
        - 分析样本：1400+条评论
        - 情感分析：使用SnowNLP进行情感得分计算（0-1分）
        - 主题分类：使用API进行评论主题分类
        
        ### 💡 使用建议
        - 点击顶部按钮切换页面
        - 在探索页面可以组合多个筛选条件进行交叉分析
        - 点击图表可以查看详细数据
        """)