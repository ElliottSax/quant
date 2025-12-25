"use client";

import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import ForceGraph2D to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-slate-900/50">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
    </div>
  ),
});

interface NetworkNode {
  id: string;
  name: string;
  party: 'Democratic' | 'Republican' | 'Independent' | string;
  centrality: number;
  tradeCount?: number;
  cluster?: number;
}

interface NetworkLink {
  source: string;
  target: string;
  correlation: number;
  significance: boolean;
}

interface NetworkGraphProps {
  nodes: NetworkNode[];
  links: NetworkLink[];
  height?: number;
  onNodeClick?: (node: NetworkNode) => void;
  onNodeHover?: (node: NetworkNode | null) => void;
  highlightedNode?: string | null;
}

const PARTY_COLORS = {
  Democratic: '#3b82f6',
  Republican: '#ef4444',
  Independent: '#a855f7',
  default: '#6b7280',
};

export function NetworkGraph({
  nodes,
  links,
  height = 600,
  onNodeClick,
  onNodeHover,
  highlightedNode,
}: NetworkGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height });
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [filterParty, setFilterParty] = useState<string | null>(null);
  const [minCorrelation, setMinCorrelation] = useState(0.3);
  const [showLabels, setShowLabels] = useState(true);

  // Handle resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height,
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [height]);

  // Filter data based on settings
  const filteredData = useMemo(() => {
    const filteredLinks = links.filter(
      (link) => Math.abs(link.correlation) >= minCorrelation
    );

    const connectedNodeIds = new Set<string>();
    filteredLinks.forEach((link) => {
      connectedNodeIds.add(typeof link.source === 'string' ? link.source : (link.source as any).id);
      connectedNodeIds.add(typeof link.target === 'string' ? link.target : (link.target as any).id);
    });

    const filteredNodes = nodes.filter((node) => {
      if (!connectedNodeIds.has(node.id)) return false;
      if (filterParty && node.party !== filterParty) return false;
      return true;
    });

    return {
      nodes: filteredNodes,
      links: filteredLinks.filter(
        (link) =>
          filteredNodes.some((n) => n.id === (typeof link.source === 'string' ? link.source : (link.source as any).id)) &&
          filteredNodes.some((n) => n.id === (typeof link.target === 'string' ? link.target : (link.target as any).id))
      ),
    };
  }, [nodes, links, filterParty, minCorrelation]);

  // Get node color based on party
  const getNodeColor = useCallback((node: NetworkNode) => {
    const baseColor = PARTY_COLORS[node.party as keyof typeof PARTY_COLORS] || PARTY_COLORS.default;
    if (hoveredNode === node.id || selectedNode === node.id || highlightedNode === node.id) {
      return baseColor;
    }
    if (hoveredNode || selectedNode) {
      // Check if connected to hovered/selected node
      const activeNode = hoveredNode || selectedNode;
      const isConnected = filteredData.links.some(
        (link) =>
          (((typeof link.source === 'string' ? link.source : (link.source as any).id) === activeNode &&
            (typeof link.target === 'string' ? link.target : (link.target as any).id) === node.id) ||
           ((typeof link.target === 'string' ? link.target : (link.target as any).id) === activeNode &&
            (typeof link.source === 'string' ? link.source : (link.source as any).id) === node.id))
      );
      return isConnected ? baseColor : `${baseColor}33`;
    }
    return baseColor;
  }, [hoveredNode, selectedNode, highlightedNode, filteredData.links]);

  // Get link color based on correlation
  const getLinkColor = useCallback((link: any) => {
    const correlation = link.correlation;
    const activeNode = hoveredNode || selectedNode;

    if (activeNode) {
      const sourceId = typeof link.source === 'string' ? link.source : (link.source as any).id;
      const targetId = typeof link.target === 'string' ? link.target : (link.target as any).id;
      if (sourceId !== activeNode && targetId !== activeNode) {
        return 'rgba(100, 100, 100, 0.1)';
      }
    }

    if (correlation > 0) {
      const intensity = Math.min(correlation, 1);
      return `rgba(34, 197, 94, ${0.3 + intensity * 0.5})`;
    } else {
      const intensity = Math.min(Math.abs(correlation), 1);
      return `rgba(239, 68, 68, ${0.3 + intensity * 0.5})`;
    }
  }, [hoveredNode, selectedNode]);

  // Get node size based on centrality
  const getNodeSize = useCallback((node: NetworkNode) => {
    const baseSize = 6;
    const maxSize = 20;
    return baseSize + node.centrality * (maxSize - baseSize);
  }, []);

  // Handle node interactions
  const handleNodeClick = useCallback((node: any) => {
    setSelectedNode(node.id === selectedNode ? null : node.id);
    onNodeClick?.(node as NetworkNode);
  }, [selectedNode, onNodeClick]);

  const handleNodeHover = useCallback((node: any) => {
    setHoveredNode(node?.id || null);
    onNodeHover?.(node as NetworkNode | null);
  }, [onNodeHover]);

  // Node canvas rendering for better performance
  const nodeCanvasObject = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const size = getNodeSize(node);
    const color = getNodeColor(node);
    const isActive = hoveredNode === node.id || selectedNode === node.id;

    // Glow effect for active nodes
    if (isActive) {
      ctx.shadowColor = color;
      ctx.shadowBlur = 15;
    }

    // Draw node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();

    // Border
    ctx.strokeStyle = isActive ? '#fff' : 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = isActive ? 2 : 1;
    ctx.stroke();

    ctx.shadowBlur = 0;

    // Label
    if (showLabels && (globalScale > 0.8 || isActive)) {
      const label = node.name.split(' ').slice(-1)[0]; // Last name only
      const fontSize = isActive ? 14 / globalScale : 10 / globalScale;
      ctx.font = `${isActive ? 'bold ' : ''}${fontSize}px Inter, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillStyle = isActive ? '#fff' : 'rgba(255, 255, 255, 0.7)';
      ctx.fillText(label, node.x, node.y + size + 3);
    }
  }, [getNodeSize, getNodeColor, hoveredNode, selectedNode, showLabels]);

  // Stats for selected/hovered node
  const activeNodeStats = useMemo(() => {
    const activeId = hoveredNode || selectedNode;
    if (!activeId) return null;

    const node = filteredData.nodes.find((n) => n.id === activeId);
    if (!node) return null;

    const connections = filteredData.links.filter(
      (link) =>
        (typeof link.source === 'string' ? link.source : (link.source as any).id) === activeId ||
        (typeof link.target === 'string' ? link.target : (link.target as any).id) === activeId
    );

    const avgCorrelation =
      connections.length > 0
        ? connections.reduce((sum, l) => sum + Math.abs(l.correlation), 0) / connections.length
        : 0;

    return {
      node,
      connectionCount: connections.length,
      avgCorrelation,
      strongConnections: connections.filter((l) => Math.abs(l.correlation) > 0.7).length,
    };
  }, [hoveredNode, selectedNode, filteredData]);

  return (
    <div className="relative bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <div>
          <h3 className="text-lg font-bold text-white">Politician Network</h3>
          <p className="text-sm text-slate-400">
            {filteredData.nodes.length} politicians · {filteredData.links.length} connections
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-4">
          {/* Party filter */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Party:</span>
            <div className="flex gap-1">
              {[null, 'Democratic', 'Republican', 'Independent'].map((party) => (
                <button
                  key={party || 'all'}
                  onClick={() => setFilterParty(party)}
                  className={`px-2 py-1 text-xs rounded transition-all ${
                    filterParty === party
                      ? party === 'Democratic'
                        ? 'bg-blue-500 text-white'
                        : party === 'Republican'
                        ? 'bg-red-500 text-white'
                        : party === 'Independent'
                        ? 'bg-purple-500 text-white'
                        : 'bg-indigo-500 text-white'
                      : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  {party || 'All'}
                </button>
              ))}
            </div>
          </div>

          {/* Correlation threshold */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Min Correlation:</span>
            <input
              type="range"
              min="0"
              max="0.9"
              step="0.1"
              value={minCorrelation}
              onChange={(e) => setMinCorrelation(parseFloat(e.target.value))}
              className="w-20 h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
            <span className="text-xs text-slate-400 w-8">{minCorrelation.toFixed(1)}</span>
          </div>

          {/* Labels toggle */}
          <button
            onClick={() => setShowLabels(!showLabels)}
            className={`px-2 py-1 text-xs rounded transition-all ${
              showLabels
                ? 'bg-indigo-500 text-white'
                : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Labels
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-6 px-4 py-2 border-b border-slate-700/50 text-xs">
        <div className="flex items-center gap-4">
          <span className="text-slate-500">Party:</span>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-slate-400">Democrat</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-slate-400">Republican</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            <span className="text-slate-400">Independent</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-slate-500">Correlation:</span>
          <div className="flex items-center gap-1.5">
            <div className="w-8 h-0.5 bg-green-500 rounded" />
            <span className="text-slate-400">Positive</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-8 h-0.5 bg-red-500 rounded" />
            <span className="text-slate-400">Negative</span>
          </div>
        </div>
      </div>

      {/* Graph */}
      <div ref={containerRef} className="relative" style={{ height: dimensions.height }}>
        {filteredData.nodes.length > 0 ? (
          <ForceGraph2D
            width={dimensions.width}
            height={dimensions.height}
            graphData={filteredData}
            nodeId="id"
            nodeLabel={(node: any) => `${node.name}\nParty: ${node.party}\nCentrality: ${(node.centrality * 100).toFixed(1)}%`}
            nodeCanvasObject={nodeCanvasObject}
            nodePointerAreaPaint={(node: any, color, ctx) => {
              ctx.fillStyle = color;
              ctx.beginPath();
              ctx.arc(node.x, node.y, getNodeSize(node) + 5, 0, 2 * Math.PI);
              ctx.fill();
            }}
            linkColor={getLinkColor}
            linkWidth={(link: any) => Math.max(1, Math.abs(link.correlation) * 3)}
            linkCurvature={0.2}
            onNodeClick={handleNodeClick}
            onNodeHover={handleNodeHover}
            cooldownTicks={100}
            d3AlphaDecay={0.02}
            d3VelocityDecay={0.3}
            backgroundColor="transparent"
            enableZoomInteraction={true}
            enablePanInteraction={true}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-slate-500">
            No connections match the current filters
          </div>
        )}

        {/* Active node info overlay */}
        {activeNodeStats && (
          <div className="absolute top-4 right-4 p-4 bg-slate-800/90 backdrop-blur-lg rounded-xl border border-slate-700/50 max-w-xs">
            <div className="flex items-center gap-3 mb-3">
              <div
                className="w-4 h-4 rounded-full"
                style={{
                  backgroundColor:
                    PARTY_COLORS[activeNodeStats.node.party as keyof typeof PARTY_COLORS] ||
                    PARTY_COLORS.default,
                }}
              />
              <div>
                <h4 className="font-semibold text-white">{activeNodeStats.node.name}</h4>
                <p className="text-xs text-slate-400">{activeNodeStats.node.party}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-slate-500 text-xs">Connections</p>
                <p className="font-semibold text-white">{activeNodeStats.connectionCount}</p>
              </div>
              <div>
                <p className="text-slate-500 text-xs">Centrality</p>
                <p className="font-semibold text-white">
                  {(activeNodeStats.node.centrality * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-slate-500 text-xs">Avg Correlation</p>
                <p className="font-semibold text-white">{activeNodeStats.avgCorrelation.toFixed(3)}</p>
              </div>
              <div>
                <p className="text-slate-500 text-xs">Strong Links</p>
                <p className="font-semibold text-indigo-400">{activeNodeStats.strongConnections}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-slate-700/50 bg-slate-800/30 text-xs text-slate-500">
        Drag to pan · Scroll to zoom · Click node to select · Node size = centrality score
      </div>
    </div>
  );
}
