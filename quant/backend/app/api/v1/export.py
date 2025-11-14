"""
Data Export API Endpoints

Research data export endpoints for downloading analysis results, raw data,
and visualizations in various formats (JSON, CSV, Excel, etc.).

**RESEARCH USE ONLY**: For academic research, transparency, and public oversight.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, date
import pandas as pd
import io
import json
from enum import Enum

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.politician import Politician
from app.models.trade import Trade
from app.api.v1.patterns import (
    load_politician_trades,
    analyze_fourier,
    analyze_regime,
    analyze_patterns,
    analyze_comprehensive
)

logger = get_logger(__name__)
router = APIRouter()


class ExportFormat(str, Enum):
    """Supported export formats"""
    json = "json"
    csv = "csv"
    excel = "xlsx"
    markdown = "md"


# ============================================================================
# Raw Data Export Endpoints
# ============================================================================

@router.get(
    "/trades/{politician_id}",
    summary="Export raw trade data",
    description="Download all trades for a politician in various formats"
)
async def export_trades(
    politician_id: str = Path(..., description="Politician UUID"),
    db: AsyncSession = Depends(get_db),
    format: ExportFormat = Query(ExportFormat.csv, description="Export format"),
    start_date: Optional[date] = Query(None, description="Filter start date"),
    end_date: Optional[date] = Query(None, description="Filter end date")
):
    """
    Export raw trade data for a politician.

    **Research Applications**:
    - Download data for external analysis (R, Python, Excel)
    - Create custom visualizations
    - Build alternative models
    - Archive for longitudinal studies

    **Formats**:
    - JSON: Structured data with all fields
    - CSV: Spreadsheet-friendly format
    - Excel: Multi-sheet workbook with metadata
    - Markdown: Human-readable format
    """

    # Load politician
    result = await db.execute(select(Politician).where(Politician.id == politician_id))
    politician = result.scalar_one_or_none()

    if not politician:
        raise HTTPException(status_code=404, detail=f"Politician {politician_id} not found")

    # Load trades
    trades_df = await load_politician_trades(db, politician_id, start_date, end_date)

    if trades_df.empty:
        raise HTTPException(status_code=404, detail="No trades found for specified criteria")

    # Export based on format
    if format == ExportFormat.json:
        # JSON format
        data = {
            'politician': {
                'id': str(politician.id),
                'name': politician.name,
                'party': politician.party,
                'state': politician.state,
                'chamber': politician.chamber
            },
            'export_date': datetime.utcnow().isoformat(),
            'trade_count': len(trades_df),
            'date_range': {
                'start': trades_df['transaction_date'].min().isoformat(),
                'end': trades_df['transaction_date'].max().isoformat()
            },
            'trades': json.loads(trades_df.to_json(orient='records', date_format='iso'))
        }

        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={
                'Content-Disposition': f'attachment; filename="{politician.name.replace(" ", "_")}_trades.json"'
            }
        )

    elif format == ExportFormat.csv:
        # CSV format
        output = io.StringIO()
        trades_df.to_csv(output, index=False)
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                'Content-Disposition': f'attachment; filename="{politician.name.replace(" ", "_")}_trades.csv"'
            }
        )

    elif format == ExportFormat.excel:
        # Excel format with multiple sheets
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Trades sheet
            trades_df.to_excel(writer, sheet_name='Trades', index=False)

            # Metadata sheet
            metadata = pd.DataFrame([{
                'Politician': politician.name,
                'Party': politician.party,
                'State': politician.state,
                'Chamber': politician.chamber,
                'Total Trades': len(trades_df),
                'First Trade': trades_df['transaction_date'].min(),
                'Last Trade': trades_df['transaction_date'].max(),
                'Export Date': datetime.utcnow()
            }])
            metadata.to_excel(writer, sheet_name='Metadata', index=False)

            # Summary statistics sheet
            summary = pd.DataFrame({
                'Ticker': trades_df.groupby('ticker').size().sort_values(ascending=False),
                'Transaction Type': trades_df.groupby('transaction_type').size()
            })
            summary.to_excel(writer, sheet_name='Summary')

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                'Content-Disposition': f'attachment; filename="{politician.name.replace(" ", "_")}_trades.xlsx"'
            }
        )

    else:  # Markdown
        # Markdown format
        md_content = f"# Trading Data: {politician.name}\n\n"
        md_content += f"**Party:** {politician.party}  \n"
        md_content += f"**State:** {politician.state}  \n"
        md_content += f"**Chamber:** {politician.chamber}  \n\n"
        md_content += f"**Total Trades:** {len(trades_df)}  \n"
        md_content += f"**Date Range:** {trades_df['transaction_date'].min().date()} to {trades_df['transaction_date'].max().date()}  \n\n"
        md_content += "## Trades\n\n"
        md_content += trades_df.to_markdown(index=False)

        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={
                'Content-Disposition': f'attachment; filename="{politician.name.replace(" ", "_")}_trades.md"'
            }
        )


@router.get(
    "/analysis/{politician_id}",
    summary="Export analysis results",
    description="Download complete pattern analysis results"
)
async def export_analysis(
    politician_id: str = Path(..., description="Politician UUID"),
    db: AsyncSession = Depends(get_db),
    format: ExportFormat = Query(ExportFormat.json, description="Export format"),
    include_fourier: bool = Query(True, description="Include Fourier analysis"),
    include_hmm: bool = Query(True, description="Include HMM regime analysis"),
    include_dtw: bool = Query(True, description="Include DTW pattern matching")
):
    """
    Export complete pattern analysis results.

    **Research Applications**:
    - Save analysis results for offline review
    - Compare analyses across time periods
    - Share findings with collaborators
    - Archive for reproducibility

    **Formats**:
    - JSON: Complete structured results
    - CSV: Tabular summaries
    - Excel: Multi-sheet with all analyses
    - Markdown: Formatted report
    """

    # Load politician
    result = await db.execute(select(Politician).where(Politician.id == politician_id))
    politician = result.scalar_one_or_none()

    if not politician:
        raise HTTPException(status_code=404, detail=f"Politician {politician_id} not found")

    # Run analyses
    analyses = {}

    try:
        if include_fourier:
            analyses['fourier'] = await analyze_fourier(politician_id, db)

        if include_hmm:
            analyses['hmm'] = await analyze_regime(politician_id, db)

        if include_dtw:
            analyses['dtw'] = await analyze_patterns(politician_id, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Analysis export failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    if not analyses:
        raise HTTPException(status_code=400, detail="No analyses selected")

    # Export based on format
    if format == ExportFormat.json:
        # Convert Pydantic models to dicts
        data = {
            'politician': {
                'id': str(politician.id),
                'name': politician.name,
                'party': politician.party,
                'state': politician.state
            },
            'export_date': datetime.utcnow().isoformat(),
            'analyses': {
                key: value.dict() if hasattr(value, 'dict') else value
                for key, value in analyses.items()
            }
        }

        return Response(
            content=json.dumps(data, indent=2, default=str),
            media_type="application/json",
            headers={
                'Content-Disposition': f'attachment; filename="{politician.name.replace(" ", "_")}_analysis.json"'
            }
        )

    elif format == ExportFormat.markdown:
        # Generate markdown report
        md = f"# Pattern Analysis Report: {politician.name}\n\n"
        md += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  \n"
        md += f"**Party:** {politician.party} | **State:** {politician.state}  \n\n"

        md += "---\n\n"

        if 'fourier' in analyses:
            fourier = analyses['fourier']
            md += "## Fourier Cycle Analysis\n\n"
            md += f"**Total Trades Analyzed:** {fourier.total_trades}  \n"
            md += f"**Date Range:** {fourier.date_range_start} to {fourier.date_range_end}  \n"
            md += f"**Cycles Found:** {fourier.total_cycles_found}  \n\n"

            if fourier.dominant_cycles:
                md += "### Dominant Cycles\n\n"
                md += "| Period (days) | Category | Strength | Confidence |\n"
                md += "|---------------|----------|----------|------------|\n"
                for cycle in fourier.dominant_cycles[:5]:
                    md += f"| {cycle.period_days:.1f} | {cycle.category} | {cycle.strength:.3f} | {cycle.confidence:.1%} |\n"
                md += "\n"

            md += f"**Summary:** {fourier.summary}\n\n"
            md += "---\n\n"

        if 'hmm' in analyses:
            hmm = analyses['hmm']
            md += "## Regime Detection (HMM)\n\n"
            md += f"**Current Regime:** {hmm.current_regime_name}  \n"
            md += f"**Confidence:** {hmm.regime_confidence:.1%}  \n"
            md += f"**Expected Duration:** {hmm.expected_duration_days:.1f} days  \n\n"

            md += "### Detected Regimes\n\n"
            md += "| Regime | Avg Return | Volatility | Frequency |\n"
            md += "|--------|------------|------------|----------|\n"
            for regime in hmm.regimes:
                md += f"| {regime.name} | {regime.avg_return:+.3f} | {regime.volatility:.3f} | {regime.frequency:.1%} |\n"
            md += "\n---\n\n"

        if 'dtw' in analyses:
            dtw = analyses['dtw']
            md += "## Pattern Matching (DTW)\n\n"
            md += f"**Current Pattern Window:** {dtw.current_pattern_days} days  \n"
            md += f"**Matches Found:** {dtw.matches_found}  \n"
            md += f"**30-Day Prediction:** {dtw.prediction_30d:+.1f} trades  \n"
            md += f"**Confidence:** {dtw.prediction_confidence:.1%}  \n\n"

            if dtw.top_matches:
                md += "### Top Historical Matches\n\n"
                md += "| Date | Similarity | 30d Outcome |\n"
                md += "|------|------------|-------------|\n"
                for match in dtw.top_matches[:5]:
                    outcome = f"{match.outcome_30d_trades:+.1f}" if match.outcome_30d_trades else "N/A"
                    md += f"| {match.match_date} | {match.similarity_score:.1%} | {outcome} |\n"
                md += "\n"

        return Response(
            content=md,
            media_type="text/markdown",
            headers={
                'Content-Disposition': f'attachment; filename="{politician.name.replace(" ", "_")}_analysis.md"'
            }
        )

    else:
        raise HTTPException(status_code=400, detail=f"Format {format} not supported for analysis export")


@router.get(
    "/batch/all-politicians",
    summary="Batch export all politicians",
    description="Export data for all politicians with sufficient trading history"
)
async def export_all_politicians(
    db: AsyncSession = Depends(get_db),
    format: ExportFormat = Query(ExportFormat.csv, description="Export format"),
    min_trades: int = Query(30, description="Minimum trades required")
):
    """
    Batch export data for all politicians meeting criteria.

    **Research Applications**:
    - Build comprehensive datasets
    - Cross-politician statistical analysis
    - Machine learning model training
    - Longitudinal studies

    **Warning**: This endpoint may take several minutes for large datasets.
    """

    # Get all politicians with sufficient trades
    query = (
        select(Politician)
        .join(Trade, Trade.politician_id == Politician.id)
        .group_by(Politician.id)
        .having(func.count(Trade.id) >= min_trades)
        .order_by(Politician.name)
    )

    result = await db.execute(query)
    politicians = result.scalars().all()

    if not politicians:
        raise HTTPException(status_code=404, detail="No politicians found matching criteria")

    # Collect all trades
    all_trades = []

    for politician in politicians:
        trades_df = await load_politician_trades(db, str(politician.id))
        if not trades_df.empty:
            trades_df['politician_id'] = str(politician.id)
            trades_df['politician_party'] = politician.party
            trades_df['politician_state'] = politician.state
            all_trades.append(trades_df)

    combined_df = pd.concat(all_trades, ignore_index=True)

    # Export
    if format == ExportFormat.csv:
        output = io.StringIO()
        combined_df.to_csv(output, index=False)
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                'Content-Disposition': 'attachment; filename="all_politicians_trades.csv"'
            }
        )

    elif format == ExportFormat.json:
        data = {
            'export_date': datetime.utcnow().isoformat(),
            'politician_count': len(politicians),
            'total_trades': len(combined_df),
            'trades': json.loads(combined_df.to_json(orient='records', date_format='iso'))
        }

        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={
                'Content-Disposition': 'attachment; filename="all_politicians_trades.json"'
            }
        )

    else:
        raise HTTPException(status_code=400, detail=f"Format {format} not supported for batch export")


@router.get(
    "/research-dataset",
    summary="Generate research dataset",
    description="Create a complete research dataset with trades and precomputed analyses"
)
async def create_research_dataset(
    db: AsyncSession = Depends(get_db),
    include_analysis: bool = Query(True, description="Include precomputed pattern analyses"),
    format: ExportFormat = Query(ExportFormat.excel, description="Export format")
):
    """
    Generate a complete research-ready dataset.

    **Contents**:
    - All politician trades
    - Precomputed Fourier cycles
    - Regime classifications
    - Pattern match predictions
    - Summary statistics
    - Metadata

    **Perfect for**:
    - Academic research papers
    - Replication studies
    - Teaching/learning
    - Public transparency

    **Warning**: Large file, may take 5-10 minutes to generate.
    """

    logger.info("Generating research dataset...")

    # This would be a comprehensive export
    # For now, return a simplified version
    raise HTTPException(
        status_code=501,
        detail="Research dataset generation in progress. Use /batch/all-politicians for now."
    )
