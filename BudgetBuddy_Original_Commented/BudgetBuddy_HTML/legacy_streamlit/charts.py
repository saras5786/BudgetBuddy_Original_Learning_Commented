# Interactive Plotly Charts with Clean Light Theme and Smooth Hover Effects

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Clean light theme palette
PALETTE = [
    "#2563eb", "#06b6d4", "#10b981", "#f59e0b",
    "#ec4899", "#8b5cf6", "#64748b", "#14b8a6",
    "#f97316", "#6366f1", "#84cc16", "#a855f7"
]

def get_base_layout(**overrides):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color="#1e293b"),
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.96)",
            bordercolor="rgba(37, 99, 235, 0.4)",
            font=dict(family="sans-serif", size=13, color="#0f172a")
        )
    )
    base.update(overrides)
    return base


def create_category_donut_chart(category_df):
    if category_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No category data available", showarrow=False, font=dict(size=14, color="#64748b"))
        fig.update_layout(get_base_layout())
        return fig

    fig = go.Figure(data=[
        go.Pie(
            labels=category_df["category"],
            values=category_df["amount"],
            hole=0.6,
            marker=dict(colors=PALETTE),
            textinfo="label+percent",
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Share: %{percent:.1%}<extra></extra>"
        )
    ])

    fig.update_layout(get_base_layout(
        showlegend=False,
        height=360,
        margin=dict(l=30, r=30, t=30, b=30)
    ))
    return fig


def create_category_bar_chart(category_df):
    if category_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No category data available", showarrow=False, font=dict(size=14, color="#64748b"))
        fig.update_layout(get_base_layout())
        return fig

    df_sorted = category_df.sort_values("amount", ascending=True)

    fig = go.Figure(data=[
        go.Bar(
            x=df_sorted["amount"],
            y=df_sorted["category"],
            orientation="h",
            marker=dict(
                color=df_sorted["amount"],
                colorscale="Blues",
                line=dict(color="rgba(37, 99, 235, 0.4)", width=1)
            ),
            hovertemplate="<b>%{y}</b><br>Total: ₹%{x:,.2f}<extra></extra>"
        )
    ])

    fig.update_layout(get_base_layout(
        height=360,
        xaxis=dict(gridcolor="rgba(226, 232, 240, 0.6)", title="Amount (₹)"),
        yaxis=dict(title="")
    ))
    return fig


def create_monthly_trend_chart(monthly_df, monthly_income=0.0):
    if monthly_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No monthly history available", showarrow=False, font=dict(size=14, color="#64748b"))
        fig.update_layout(get_base_layout())
        return fig

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=monthly_df["month"],
        y=monthly_df["amount"],
        name="Expenses",
        marker=dict(color="rgba(37, 99, 235, 0.85)", line=dict(color="#2563eb", width=1.5)),
        hovertemplate="<b>%{x}</b><br>Expenses: ₹%{y:,.2f}<extra></extra>"
    ))

    if monthly_income > 0:
        fig.add_trace(go.Scatter(
            x=monthly_df["month"],
            y=[monthly_income] * len(monthly_df),
            name="Income Baseline",
            mode="lines",
            line=dict(color="#10b981", width=2.5, dash="dot"),
            hovertemplate="Income Target: ₹%{y:,.2f}<extra></extra>"
        ))

    fig.update_layout(get_base_layout(
        height=340,
        xaxis=dict(gridcolor="rgba(226, 232, 240, 0.6)", title="Month"),
        yaxis=dict(gridcolor="rgba(226, 232, 240, 0.6)", title="Amount (₹)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    ))
    return fig


def create_cumulative_savings_chart(monthly_df, monthly_income=0.0):
    if monthly_df.empty or monthly_income <= 0:
        fig = go.Figure()
        fig.add_annotation(text="Configure income to view cumulative savings trajectory", showarrow=False, font=dict(size=13, color="#64748b"))
        fig.update_layout(get_base_layout(height=280))
        return fig

    df = monthly_df.copy()
    df["net_savings"] = monthly_income - df["amount"]
    df["cumulative_savings"] = df["net_savings"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"],
        y=df["cumulative_savings"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.12)",
        line=dict(color="#10b981", width=3),
        marker=dict(size=6, color="#059669"),
        hovertemplate="<b>%{x}</b><br>Cumulative Savings: ₹%{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(get_base_layout(
        height=280,
        xaxis=dict(gridcolor="rgba(226, 232, 240, 0.6)", title="Month"),
        yaxis=dict(gridcolor="rgba(226, 232, 240, 0.6)", title="Cumulative Savings (₹)")
    ))
    return fig


def create_wide_yearly_comparison_chart(yearly_df):
    if yearly_df.empty:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=yearly_df["Year"].astype(str),
        y=yearly_df["Total_Income"],
        name="Income",
        marker_color="#10b981",
        hovertemplate="<b>%{x}</b><br>Income: ₹%{y:,.2f}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=yearly_df["Year"].astype(str),
        y=yearly_df["Total_Expenses"],
        name="Expenses",
        marker_color="#ef4444",
        hovertemplate="<b>%{x}</b><br>Expenses: ₹%{y:,.2f}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=yearly_df["Year"].astype(str),
        y=yearly_df["Net_Savings"],
        name="Net Balance",
        marker_color="#3b82f6",
        hovertemplate="<b>%{x}</b><br>Net Balance: ₹%{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(get_base_layout(
        barmode="group",
        height=380,
        xaxis=dict(title="Year", gridcolor="rgba(226, 232, 240, 0.6)"),
        yaxis=dict(title="Amount (₹)", gridcolor="rgba(226, 232, 240, 0.6)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    ))
    return fig


def create_wide_monthly_chart(monthly_df):
    if monthly_df.empty:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly_df["YearMonth"],
        y=monthly_df["Total_Expenses"],
        mode="lines",
        name="Expenses",
        line=dict(color="#ef4444", width=2),
        fill="tozeroy",
        fillcolor="rgba(239, 68, 68, 0.08)",
        hovertemplate="<b>%{x}</b><br>Expense: ₹%{y:,.2f}<extra></extra>"
    ))

    if "Total_Income" in monthly_df.columns and monthly_df["Total_Income"].sum() > 0:
        fig.add_trace(go.Scatter(
            x=monthly_df["YearMonth"],
            y=monthly_df["Total_Income"],
            mode="lines+markers",
            name="Income",
            line=dict(color="#10b981", width=2.5),
            marker=dict(size=4),
            hovertemplate="<b>%{x}</b><br>Income: ₹%{y:,.2f}<extra></extra>"
        ))

    fig.update_layout(get_base_layout(
        height=340,
        xaxis=dict(title="Timeline", gridcolor="rgba(226, 232, 240, 0.6)"),
        yaxis=dict(title="Amount (₹)", gridcolor="rgba(226, 232, 240, 0.6)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    ))
    return fig


def create_correlation_heatmap(df):
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        fig = go.Figure()
        fig.add_annotation(text="At least 2 numerical columns required for correlation matrix", showarrow=False)
        fig.update_layout(get_base_layout(height=300))
        return fig

    corr = numeric_df.corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale="Blues",
        zmin=-1,
        zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont={"size": 11},
        hovertemplate="<b>%{x} vs %{y}</b><br>Correlation: %{z:.2f}<extra></extra>"
    ))

    fig.update_layout(get_base_layout(
        height=450,
        margin=dict(l=40, r=40, t=30, b=40)
    ))
    return fig


def create_custom_chart(df, chart_type, x_col, y_col=None, color_col=None):
    if df.empty or not x_col:
        fig = go.Figure()
        fig.add_annotation(text="Select columns to render chart", showarrow=False)
        fig.update_layout(get_base_layout(height=360))
        return fig

    color = color_col if color_col and color_col != "None" else None

    if chart_type == "Bar":
        fig = px.bar(df, x=x_col, y=y_col, color=color, color_discrete_sequence=PALETTE)
    elif chart_type == "Line":
        fig = px.line(df, x=x_col, y=y_col, color=color, color_discrete_sequence=PALETTE, markers=True)
    elif chart_type == "Scatter":
        fig = px.scatter(df, x=x_col, y=y_col, color=color, color_discrete_sequence=PALETTE)
    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x_col, y=y_col, color=color, color_discrete_sequence=PALETTE)
    elif chart_type == "Box":
        fig = px.box(df, x=x_col, y=y_col, color=color, color_discrete_sequence=PALETTE)
    elif chart_type == "Area":
        fig = px.area(df, x=x_col, y=y_col, color=color, color_discrete_sequence=PALETTE)
    else:
        fig = px.bar(df, x=x_col, y=y_col, color=color, color_discrete_sequence=PALETTE)

    fig.update_layout(get_base_layout(
        height=420,
        xaxis=dict(gridcolor="rgba(226, 232, 240, 0.6)"),
        yaxis=dict(gridcolor="rgba(226, 232, 240, 0.6)")
    ))
    return fig
