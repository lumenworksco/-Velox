import { useEffect, useRef } from 'react'
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time } from 'lightweight-charts'

interface CandlestickChartProps {
  data: CandlestickData<Time>[]
  symbol: string
}

export default function CandlestickChart({ data, symbol }: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)

  useEffect(() => {
    if (!chartContainerRef.current) return

    const container = chartContainerRef.current
    const width = container.clientWidth
    const height = container.clientHeight || 400

    // Create chart with new color scheme
    const chart = createChart(container, {
      width,
      height,
      layout: {
        background: { color: '#0d1117' },
        textColor: '#8b949e',
      },
      grid: {
        vertLines: { color: '#30363d' },
        horzLines: { color: '#30363d' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#30363d',
      },
      timeScale: {
        borderColor: '#30363d',
        timeVisible: true,
        secondsVisible: false,
      },
    })

    // Create candlestick series with new colors
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#3fb950',
      downColor: '#f85149',
      borderDownColor: '#f85149',
      borderUpColor: '#3fb950',
      wickDownColor: '#f85149',
      wickUpColor: '#3fb950',
    })

    chartRef.current = chart
    seriesRef.current = candlestickSeries

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        const newWidth = chartContainerRef.current.clientWidth
        const newHeight = chartContainerRef.current.clientHeight || 400
        chart.applyOptions({
          width: newWidth,
          height: newHeight,
        })
      }
    }

    const resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(container)

    window.addEventListener('resize', handleResize)

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  // Update data when it changes
  useEffect(() => {
    if (seriesRef.current && data.length > 0) {
      seriesRef.current.setData(data)
      chartRef.current?.timeScale().fitContent()
    }
  }, [data])

  return (
    <div style={{ position: 'relative', height: '100%', width: '100%' }}>
      <div style={{
        position: 'absolute',
        top: '16px',
        left: '16px',
        zIndex: 10,
        backgroundColor: 'rgba(22, 27, 34, 0.9)',
        backdropFilter: 'blur(8px)',
        padding: '12px 16px',
        borderRadius: '6px',
        border: '1px solid #30363d'
      }}>
        <div style={{ color: '#c9d1d9', fontWeight: 700, fontSize: '16px' }}>{symbol}</div>
        {data.length > 0 && (
          <div style={{ color: '#8b949e', fontSize: '12px', marginTop: '4px', fontFamily: 'monospace' }}>
            O: ${data[data.length - 1].open.toFixed(2)} H: ${data[data.length - 1].high.toFixed(2)} L: ${data[data.length - 1].low.toFixed(2)} C: ${data[data.length - 1].close.toFixed(2)}
          </div>
        )}
      </div>
      <div ref={chartContainerRef} style={{ borderRadius: '6px', overflow: 'hidden', height: '100%' }} />
    </div>
  )
}
