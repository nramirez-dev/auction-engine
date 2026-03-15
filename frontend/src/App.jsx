import { useState, useRef, useEffect, useCallback } from 'react'

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const S = {
  page: {
    minHeight: '100vh',
    backgroundColor: '#0f0f0f',
    color: '#ffffff',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    padding: '2rem',
    boxSizing: 'border-box',
  },
  header: {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#ffffff',
    marginBottom: '1.5rem',
    letterSpacing: '-0.02em',
  },
  tabBar: {
    display: 'flex',
    gap: '0.25rem',
    marginBottom: '2rem',
    borderBottom: '1px solid #2a2a2a',
    paddingBottom: '0',
  },
  tab: (active) => ({
    padding: '0.6rem 1.25rem',
    fontSize: '0.875rem',
    fontWeight: 600,
    cursor: 'pointer',
    border: 'none',
    borderRadius: '8px 8px 0 0',
    backgroundColor: active ? '#1a1a1a' : 'transparent',
    color: active ? '#ffffff' : '#666666',
    borderBottom: active ? '2px solid #3b82f6' : '2px solid transparent',
    transition: 'color 0.15s',
  }),
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
    gap: '1.5rem',
  },
  card: {
    backgroundColor: '#1a1a1a',
    borderRadius: '12px',
    padding: '24px',
    border: '1px solid #2a2a2a',
  },
  cardTitle: {
    fontSize: '0.75rem',
    fontWeight: 600,
    color: '#888888',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    marginBottom: '1.25rem',
  },
  label: {
    display: 'block',
    fontSize: '0.8rem',
    color: '#888888',
    marginBottom: '0.35rem',
  },
  input: {
    width: '100%',
    backgroundColor: '#111111',
    border: '1px solid #2a2a2a',
    borderRadius: '8px',
    color: '#ffffff',
    fontSize: '0.9rem',
    padding: '0.6rem 0.75rem',
    marginBottom: '1rem',
    outline: 'none',
    boxSizing: 'border-box',
  },
  textarea: {
    width: '100%',
    backgroundColor: '#111111',
    border: '1px solid #2a2a2a',
    borderRadius: '8px',
    color: '#ffffff',
    fontSize: '0.9rem',
    padding: '0.6rem 0.75rem',
    marginBottom: '1rem',
    outline: 'none',
    boxSizing: 'border-box',
    resize: 'vertical',
    minHeight: '80px',
  },
  row: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    marginTop: '0.5rem',
  },
  btn: (color = '#3b82f6', disabled = false) => ({
    backgroundColor: disabled ? '#2a2a2a' : color,
    color: disabled ? '#666666' : '#ffffff',
    border: 'none',
    borderRadius: '8px',
    padding: '0.6rem 1.2rem',
    fontSize: '0.875rem',
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
    whiteSpace: 'nowrap',
  }),
  btnSm: (color = '#3b82f6') => ({
    backgroundColor: color,
    color: '#ffffff',
    border: 'none',
    borderRadius: '6px',
    padding: '0.4rem 0.9rem',
    fontSize: '0.8rem',
    fontWeight: 600,
    cursor: 'pointer',
    whiteSpace: 'nowrap',
  }),
  badge: (connected) => ({
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.35rem',
    fontSize: '0.8rem',
    fontWeight: 600,
    color: connected ? '#22c55e' : '#888888',
    backgroundColor: 'transparent',
    borderRadius: '999px',
    padding: '0.25rem 0',
  }),
  dot: (connected) => ({
    width: 6,
    height: 6,
    borderRadius: '50%',
    backgroundColor: connected ? '#22c55e' : '#555555',
    display: 'inline-block',
    flexShrink: 0,
  }),
  btnDisconnect: {
    backgroundColor: '#2a2a2a',
    color: '#ffffff',
    border: 'none',
    borderRadius: '8px',
    padding: '0.6rem 1.2rem',
    fontSize: '0.875rem',
    fontWeight: 600,
    cursor: 'pointer',
    whiteSpace: 'nowrap',
  },
  btnFullWidth: (disabled = false) => ({
    width: '100%',
    backgroundColor: disabled ? '#2a2a2a' : '#3b82f6',
    color: disabled ? '#666666' : '#ffffff',
    border: 'none',
    borderRadius: '8px',
    padding: '0.7rem 1.2rem',
    fontSize: '0.875rem',
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
  }),
  bigBid: (flash) => ({
    fontSize: '3.5rem',
    fontWeight: 800,
    color: flash ? '#60a5fa' : '#3b82f6',
    letterSpacing: '-0.03em',
    lineHeight: 1,
    transition: 'color 0.4s ease',
    marginBottom: '0.5rem',
  }),
  bidLabel: {
    fontSize: '0.8rem',
    color: '#888888',
  },
  historyList: {
    listStyle: 'none',
    margin: 0,
    padding: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  historyItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#222222',
    borderRadius: '8px',
    padding: '0.6rem 0.75rem',
    fontSize: '0.85rem',
  },
  historyAmount: {
    fontWeight: 700,
    color: '#22c55e',
  },
  historyMeta: {
    color: '#888888',
    fontSize: '0.75rem',
    textAlign: 'right',
  },
  feedback: (ok) => ({
    marginTop: '0.75rem',
    padding: '0.6rem 0.75rem',
    borderRadius: '8px',
    fontSize: '0.85rem',
    fontWeight: 500,
    color: ok ? '#22c55e' : '#ef4444',
    backgroundColor: ok ? '#052e1633' : '#2d0a0a55',
  }),
  empty: {
    color: '#555555',
    fontSize: '0.85rem',
    textAlign: 'center',
    padding: '1rem 0',
  },
  productCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: '10px',
    padding: '1rem 1.25rem',
    border: '1px solid #2a2a2a',
    marginBottom: '0.75rem',
  },
  productTitle: {
    fontWeight: 700,
    fontSize: '0.95rem',
    color: '#ffffff',
    marginBottom: '0.25rem',
  },
  productMeta: {
    fontSize: '0.8rem',
    color: '#888888',
    marginBottom: '0.75rem',
  },
  successBox: {
    backgroundColor: '#052e1633',
    border: '1px solid #2a2a2a',
    borderRadius: '10px',
    padding: '1rem 1.25rem',
    marginTop: '1rem',
  },
  successTitle: {
    fontSize: '0.75rem',
    fontWeight: 600,
    color: '#22c55e',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    marginBottom: '0.5rem',
  },
  codeBlock: {
    fontFamily: 'monospace',
    fontSize: '0.8rem',
    color: '#888888',
    wordBreak: 'break-all',
    marginBottom: '0.75rem',
  },
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const DEFAULT_OWNER_ID = crypto.randomUUID()

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
}

function shortId(id) {
  return id ? `${id.slice(0, 8)}…` : '—'
}

function fmtPrice(v) {
  return `$${parseFloat(v).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
}

// ---------------------------------------------------------------------------
// Tab: Live Auction
// ---------------------------------------------------------------------------

function LiveAuctionTab({ initialAuctionId }) {
  const [auctionId, setAuctionId] = useState(initialAuctionId || '')
  const [userId, setUserId] = useState(DEFAULT_OWNER_ID)
  const [connected, setConnected] = useState(false)
  const [currentBid, setCurrentBid] = useState(null)
  const [flash, setFlash] = useState(false)
  const [history, setHistory] = useState([])
  const [bidAmount, setBidAmount] = useState('')
  const [feedback, setFeedback] = useState(null)
  const wsRef = useRef(null)

  // Sync if parent passes a new auction ID (after Create Auction)
  useEffect(() => {
    if (initialAuctionId) setAuctionId(initialAuctionId)
  }, [initialAuctionId])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.onclose = null
      wsRef.current.close()
      wsRef.current = null
    }
    setConnected(false)
  }, [])

  const connect = useCallback(async () => {
    if (!auctionId.trim() || !userId.trim()) return
    disconnect()
    setCurrentBid(null)
    setHistory([])

    const ticketRes = await fetch(`/api/v1/ws-ticket?user_id=${encodeURIComponent(userId)}`)
    if (!ticketRes.ok) {
      setFeedback({ ok: false, msg: 'Failed to get WS ticket' })
      return
    }
    const { ticket } = await ticketRes.json()

    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${proto}://${location.host}/ws/auction/${auctionId}?ticket=${ticket}`)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.amount != null) {
        setCurrentBid(msg.amount)
        setFlash(true)
        setTimeout(() => setFlash(false), 500)
        setHistory((prev) => [msg, ...prev].slice(0, 10))
      }
    }
    ws.onclose = () => setConnected(false)
    ws.onerror = () => setConnected(false)
  }, [auctionId, userId, disconnect])

  useEffect(() => () => disconnect(), [disconnect])

  const placeBid = async () => {
    if (!bidAmount || !auctionId || !userId) return
    setFeedback(null)
    const res = await fetch('/api/v1/place-bid', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Idempotency-Key': crypto.randomUUID() },
      body: JSON.stringify({ auction_id: auctionId, user_id: userId, amount: parseFloat(bidAmount) }),
    })
    const data = await res.json()
    if (res.ok) {
      setFeedback({ ok: true, msg: `Bid of ${fmtPrice(data.amount)} placed successfully` })
      setBidAmount('')
    } else {
      setFeedback({ ok: false, msg: data.error || 'Bid failed' })
    }
  }

  return (
    <div style={S.grid}>
      {/* Connection panel */}
      <div style={S.card}>
        <div style={S.cardTitle}>Connection</div>
        <label style={S.label}>Auction ID</label>
        <input style={S.input} placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          value={auctionId} onChange={(e) => setAuctionId(e.target.value)} disabled={connected} />
        <label style={S.label}>User ID</label>
        <input style={S.input} placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          value={userId} onChange={(e) => setUserId(e.target.value)} disabled={connected} />
        <div style={S.row}>
          {connected
            ? <button style={S.btnDisconnect} onClick={disconnect}>Disconnect</button>
            : <button style={S.btn()} onClick={connect}>Connect</button>}
          <span style={S.badge(connected)}>
            <span style={S.dot(connected)} />
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Current high bid */}
      <div style={S.card}>
        <div style={S.cardTitle}>Current High Bid</div>
        <div style={S.bigBid(flash)}>
          {currentBid != null ? fmtPrice(currentBid) : '—'}
        </div>
        <div style={S.bidLabel}>Updates in real time via WebSocket</div>
      </div>

      {/* Place bid */}
      <div style={S.card}>
        <div style={S.cardTitle}>Place a Bid</div>
        <label style={S.label}>Amount (USD)</label>
        <input style={S.input} type="number" min="0" step="0.01" placeholder="0.00"
          value={bidAmount} onChange={(e) => setBidAmount(e.target.value)} />
        <button style={S.btnFullWidth()} onClick={placeBid}>Submit Bid</button>
        {feedback && <div style={S.feedback(feedback.ok)}>{feedback.msg}</div>}
      </div>

      {/* Bid history */}
      <div style={S.card}>
        <div style={S.cardTitle}>Bid History (last 10)</div>
        {history.length === 0
          ? <div style={S.empty}>No bids yet</div>
          : (
            <ul style={S.historyList}>
              {history.map((b, i) => (
                <li key={i} style={S.historyItem}>
                  <span style={S.historyAmount}>{fmtPrice(b.amount)}</span>
                  <span style={S.historyMeta}>
                    <div>{shortId(b.user_id)}</div>
                    <div>{b.placed_at ? formatTime(b.placed_at) : ''}</div>
                  </span>
                </li>
              ))}
            </ul>
          )}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Tab: Create Auction
// ---------------------------------------------------------------------------

function CreateAuctionTab({ onCreated }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [startingPrice, setStartingPrice] = useState('')
  const [ownerId, setOwnerId] = useState(DEFAULT_OWNER_ID)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null) // { productId, auctionId } | null
  const [error, setError] = useState(null)

  const submit = async () => {
    if (!title.trim() || !startingPrice || !ownerId.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    // Step 1 — create product
    const prodRes = await fetch('/api/v1/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ owner_id: ownerId, title, description: description || null, starting_price: parseFloat(startingPrice) }),
    })
    if (!prodRes.ok) {
      const d = await prodRes.json()
      setError(d.error || 'Failed to create product')
      setLoading(false)
      return
    }
    const product = await prodRes.json()

    // Step 2 — create auction
    const aucRes = await fetch('/api/v1/auctions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: product.id, owner_id: ownerId }),
    })
    if (!aucRes.ok) {
      const d = await aucRes.json()
      setError(d.error || 'Failed to create auction')
      setLoading(false)
      return
    }
    const auction = await aucRes.json()

    setResult({ productId: product.id, auctionId: auction.id })
    setLoading(false)
    setTitle('')
    setDescription('')
    setStartingPrice('')
  }

  const goLive = () => {
    if (result) onCreated(result.auctionId)
  }

  return (
    <div style={{ maxWidth: 560 }}>
      <div style={S.card}>
        <div style={S.cardTitle}>New Product & Auction</div>

        <label style={S.label}>Product Title</label>
        <input style={S.input} placeholder="e.g. Vintage Watch" value={title} onChange={(e) => setTitle(e.target.value)} />

        <label style={S.label}>Description (optional)</label>
        <textarea style={S.textarea} placeholder="Describe the item…" value={description} onChange={(e) => setDescription(e.target.value)} />

        <label style={S.label}>Starting Price (USD)</label>
        <input style={S.input} type="number" min="0" step="0.01" placeholder="0.00" value={startingPrice} onChange={(e) => setStartingPrice(e.target.value)} />

        <label style={S.label}>Owner ID</label>
        <input style={S.input} value={ownerId} onChange={(e) => setOwnerId(e.target.value)} />

        <button style={S.btn('#3b82f6', loading)} onClick={submit} disabled={loading}>
          {loading ? 'Creating…' : 'Create & Start Auction'}
        </button>

        {error && <div style={S.feedback(false)}>{error}</div>}

        {result && (
          <div style={S.successBox}>
            <div style={S.successTitle}>Auction Created</div>
            <div style={{ ...S.label, marginBottom: '0.25rem' }}>Auction ID</div>
            <div style={S.codeBlock}>{result.auctionId}</div>
            <div style={S.row}>
              <button style={S.btnSm('#3b82f6')} onClick={() => navigator.clipboard.writeText(result.auctionId)}>
                Copy ID
              </button>
              <button style={S.btnSm('#059669')} onClick={goLive}>
                Go to Live Auction →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Tab: My Products
// ---------------------------------------------------------------------------

function MyProductsTab() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [ownerId] = useState(DEFAULT_OWNER_ID)
  const [auctionResults, setAuctionResults] = useState({}) // productId → { auctionId } | { error }

  const load = useCallback(async () => {
    setLoading(true)
    const res = await fetch('/api/v1/products')
    if (res.ok) setProducts(await res.json())
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  const startAuction = async (product) => {
    setAuctionResults((prev) => ({ ...prev, [product.id]: null }))
    const res = await fetch('/api/v1/auctions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: product.id, owner_id: product.owner_id }),
    })
    const data = await res.json()
    if (res.ok) {
      setAuctionResults((prev) => ({ ...prev, [product.id]: { auctionId: data.id } }))
    } else {
      setAuctionResults((prev) => ({ ...prev, [product.id]: { error: data.error || 'Failed to start auction' } }))
    }
  }

  return (
    <div style={{ maxWidth: 680 }}>
      <div style={{ ...S.row, marginBottom: '1.5rem', marginTop: 0 }}>
        <button style={S.btn()} onClick={load} disabled={loading}>{loading ? 'Loading…' : 'Refresh'}</button>
        <span style={{ color: '#6b7280', fontSize: '0.8rem' }}>{products.length} product{products.length !== 1 ? 's' : ''}</span>
      </div>

      {products.length === 0 && !loading && (
        <div style={{ ...S.card, ...S.empty }}>No products found. Create one in the "Create Auction" tab.</div>
      )}

      {products.map((p) => {
        const ar = auctionResults[p.id]
        return (
          <div key={p.id} style={S.productCard}>
            <div style={S.productTitle}>{p.title}</div>
            <div style={S.productMeta}>
              Starting price: {fmtPrice(p.starting_price)} · Created {formatDate(p.created_at)}
            </div>
            {p.description && (
              <div style={{ ...S.productMeta, marginBottom: '0.75rem' }}>{p.description}</div>
            )}
            <div style={{ ...S.row, marginTop: 0 }}>
              <button style={S.btnSm('#3b82f6')} onClick={() => startAuction(p)}>
                Start Auction
              </button>
              <span style={{ color: '#4b5563', fontSize: '0.75rem', fontFamily: 'monospace' }}>
                {shortId(p.id)}
              </span>
            </div>
            {ar?.auctionId && (
              <div style={{ ...S.successBox, marginTop: '0.75rem' }}>
                <div style={S.successTitle}>Auction Started</div>
                <div style={S.codeBlock}>{ar.auctionId}</div>
                <button style={S.btnSm('#3b82f6')} onClick={() => navigator.clipboard.writeText(ar.auctionId)}>
                  Copy ID
                </button>
              </div>
            )}
            {ar?.error && <div style={{ ...S.feedback(false), marginTop: '0.5rem' }}>{ar.error}</div>}
          </div>
        )
      })}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Root
// ---------------------------------------------------------------------------

const TABS = ['Live Auction', 'Create Auction', 'My Products']

export default function App() {
  const [activeTab, setActiveTab] = useState(0)
  const [pendingAuctionId, setPendingAuctionId] = useState(null)

  const handleAuctionCreated = (auctionId) => {
    setPendingAuctionId(auctionId)
    setActiveTab(0)
  }

  return (
    <div style={S.page}>
      <div style={S.header}>Auction Live Dashboard</div>

      <div style={S.tabBar}>
        {TABS.map((t, i) => (
          <button key={t} style={S.tab(activeTab === i)} onClick={() => setActiveTab(i)}>{t}</button>
        ))}
      </div>

      {activeTab === 0 && <LiveAuctionTab initialAuctionId={pendingAuctionId} />}
      {activeTab === 1 && <CreateAuctionTab onCreated={handleAuctionCreated} />}
      {activeTab === 2 && <MyProductsTab />}
    </div>
  )
}
