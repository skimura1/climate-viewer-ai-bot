import { useState, useEffect, useRef } from 'react'
import { MessageCircle, X, Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import type { ActiveLayersState, MapBounds, BasemapConfig } from '@/config/types'
import { GWI_LAYERS } from '@/config/wmslayers'
import { BASEMAP_CONFIGS } from '@/config/basemaps'

interface Message {
  id: string
  content: string
  role: 'user' | 'bot'
  timestamp: Date
}

interface MapState {
  active_layers: string[]
  available_layers: string[]
  foot_increment: string
  map_position: MapBounds
  zoom_level: number
  basemap_name: string
  available_basemaps: string[]
}

interface MapAction {
  type: string
  parameters: Record<string, any>
}

interface ChatProps {
  activeLayers: ActiveLayersState
  toggleLayer: (layerId: string, isActive: boolean) => void
  mapPosition: MapBounds
  zoomLevel: number
  setMapPosition: (position: MapBounds) => void
  setZoomLevel: (zoomLevel: number) => void
  setSelectedBasemap: (basemap: BasemapConfig) => void
  selectedBasemap: BasemapConfig
}

const Chat = ({ activeLayers, toggleLayer, mapPosition, zoomLevel, setMapPosition, setZoomLevel, setSelectedBasemap, selectedBasemap }: ChatProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your climate data assistant. How can I help you explore the map data today?',
      role: 'bot',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  
  // Add refs for scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const handleMapActions = (mapActions: MapAction[]) => {
    // TODO: handle zoom level, map position, change level increment from the backend
    mapActions.forEach((action) => {
      const { layer_name, bounds, zoom_level, basemap_id, reason } = action.parameters;
      
      switch (action.type) {
        case 'add_layer':
          toggleLayer(layer_name, true);
          break;
        case 'remove_layer':
          toggleLayer(layer_name, false);
          break;
        case 'set_bounds':
          setMapPosition(bounds)
          break;
        case 'set_zoom_level':
          setZoomLevel(zoom_level)
          break;
        case 'clear_layers':
          Object.keys(activeLayers).forEach(layer => toggleLayer(layer, false))
          break;
        case 'change_basemap':
          const basemap = BASEMAP_CONFIGS.find(basemap => basemap.id === basemap_id)
          if (basemap) {
            setSelectedBasemap(basemap)
          }
          break;
      }
    })
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date()
    }
    
    setInputMessage('')
    console.log(mapPosition)

    const mapState: MapState = {
      active_layers: Object.keys(activeLayers).filter(layer => activeLayers[layer]),
      available_layers: GWI_LAYERS.map(layer => layer.layers),
      foot_increment: '100',
      map_position: mapPosition,
      zoom_level: zoomLevel,
      basemap_name: selectedBasemap.id,
      available_basemaps: BASEMAP_CONFIGS.map(basemap => basemap.id)
      }

    setMessages(prev => [...prev, userMessage])

    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: inputMessage, map_state: mapState })
    })
    const data = await response.json()

    handleMapActions(data.map_actions);

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: data.response,
      role: 'bot',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, botMessage])

  }


  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }

  return (
    <div className="fixed bottom-5 right-4 z-[1001]">
      {!isOpen ? (
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="rounded-full shadow-lg"
        >
          <MessageCircle className="h-5 w-5" />
          Chat
        </Button>
      ) : (
        <div className="flex flex-col h-[400px] p-0 bg-white rounded-lg shadow-lg">
            <div className="flex items-center justify-between p-4">
              Climate Assistant
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            {/* Divider */}
            <div className="border-t"></div>
            {/* Chat messages */}
            <ScrollArea className="flex-1 px-4 min-h-0">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      'flex',
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    )}
                  >
                    <div
                      className={cn(
                        'max-w-[80%] rounded-lg px-3 py-2 text-sm',
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground'
                      )}
                    >
                      {message.content}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
            {/* Divider */}
            <div className="border-t"></div>
            {/* Input */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about climate data..."
                  className="flex-1"
                />
                <Button onClick={handleSendMessage} size="icon">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
        </div>
      )}
    </div>
  )
}

export default Chat