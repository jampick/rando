import { useState, useEffect, useRef } from 'react'
import { WebSocketMessage, PriceUpdateMessage, AuctionStatusMessage } from '../types'

export const useWebSocket = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/ws')
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setSocket(ws)
      }
      
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        setSocket(null)
        
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, 3000)
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Error creating WebSocket:', error)
    }
  }

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (socket) {
      socket.close()
    }
  }

  const subscribe = (topics: number[]) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify({
        type: 'subscribe',
        topics
      }))
    }
  }

  const unsubscribe = (topics: number[]) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify({
        type: 'unsubscribe',
        topics
      }))
    }
  }

  useEffect(() => {
    connect()
    
    return () => {
      disconnect()
    }
  }, [])

  return {
    socket,
    isConnected,
    lastMessage,
    subscribe,
    unsubscribe,
    connect,
    disconnect
  }
}

export const usePriceUpdates = (topicIds: number[]) => {
  const { subscribe, unsubscribe, lastMessage } = useWebSocket()
  const [priceUpdates, setPriceUpdates] = useState<Map<number, PriceUpdateMessage>>(new Map())

  useEffect(() => {
    if (topicIds.length > 0) {
      subscribe(topicIds)
    }

    return () => {
      if (topicIds.length > 0) {
        unsubscribe(topicIds)
      }
    }
  }, [topicIds, subscribe, unsubscribe])

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'price_update') {
      const priceUpdate = lastMessage as PriceUpdateMessage
      setPriceUpdates(prev => new Map(prev.set(priceUpdate.topic_id, priceUpdate)))
    }
  }, [lastMessage])

  return priceUpdates
}

export const useAuctionStatus = () => {
  const { lastMessage } = useWebSocket()
  const [auctionStatus, setAuctionStatus] = useState<AuctionStatusMessage | null>(null)

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'auction_status') {
      setAuctionStatus(lastMessage as AuctionStatusMessage)
    }
  }, [lastMessage])

  return auctionStatus
}
