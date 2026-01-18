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

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 500,
      layout: {
        background: { color: '#131722' },
        textColor: '#848E9C',
      },
      grid: {
        vertLines: { color: '#2A2E39' },
        horzLines: { color: '#2A2E39' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#2A2E39',
      },
      timeScale: {
        borderColor: '#2A2E39',
        timeVisible: true,
        secondsVisible: false,
      },
    })

    // Create candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26A69A',
      downColor: '#EF5350',
      borderDownColor: '#EF5350',
      borderUpColor: '#26A69A',
      wickDownColor: '#EF5350',
      wickUpColor: '#26A69A',
    })

    chartRef.current = chart
    seriesRef.current = candlestickSeries

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
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
    <div className="relative">
      <div className="absolute top-4 left-4 z-10 bg-primary-elevated/90 backdrop-blur px-4 py-2 rounded-lg border border-primary-border">
        <div className="text-text-primary font-bold text-lg">{symbol}</div>
        {data.length > 0 && (
          <div className="text-text-secondary text-sm mt-1">
            O: ${data[data.length - 1].open.toFixed(2)} H: ${data[data.length - 1].high.toFixed(2)} L: ${data[data.length - 1].low.toFixed(2)} C: ${data[data.length - 1].close.toFixed(2)}
          </div>
        )}
      </div>
      <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />
    </div>
  )
}
