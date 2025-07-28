import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Eye, Trash2, Calendar, MapPin, DollarSign } from 'lucide-react';
import { handsService } from '../lib/api';

export default function HandsHistory() {
  const [hands, setHands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedHand, setSelectedHand] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHands();
  }, []);

  const loadHands = async () => {
    try {
      setLoading(true);
      const handsData = await handsService.getMyHands();
      setHands(handsData);
    } catch (error) {
      setError('Erro ao carregar histórico de mãos');
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteHand = async (handId) => {
    if (!confirm('Tem certeza que deseja deletar esta mão?')) return;

    try {
      await handsService.deleteHand(handId);
      setHands(hands.filter(hand => hand.id !== handId));
    } catch (error) {
      setError('Erro ao deletar mão');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getPositionColor = (position) => {
    const colors = {
      'BTN': 'bg-green-500',
      'SB': 'bg-yellow-500',
      'BB': 'bg-red-500',
      'EP': 'bg-blue-500',
      'MP': 'bg-purple-500',
      'LP': 'bg-orange-500',
    };
    return colors[position] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-slate-400">Carregando histórico...</div>
        </CardContent>
      </Card>
    );
  }

  if (hands.length === 0) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="flex flex-col items-center justify-center py-8 space-y-4">
          <div className="text-slate-400 text-center">
            <h3 className="text-lg font-medium mb-2">Nenhuma mão encontrada</h3>
            <p>Faça upload de um arquivo de hand history para começar a análise.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded">
          {error}
        </div>
      )}

      <div className="grid gap-4">
        {hands.map((hand) => (
          <Card key={hand.id} className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium text-white">Mão #{hand.hand_id}</h3>
                      {hand.hero_position && (
                        <Badge className={`${getPositionColor(hand.hero_position)} text-white text-xs`}>
                          {hand.hero_position}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-slate-400">
                      {hand.tournament_id && (
                        <div className="flex items-center space-x-1">
                          <MapPin className="h-3 w-3" />
                          <span>Torneio #{hand.tournament_id}</span>
                        </div>
                      )}
                      {hand.date_played && (
                        <div className="flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>{formatDate(hand.date_played)}</span>
                        </div>
                      )}
                      {hand.pot_size && (
                        <div className="flex items-center space-x-1">
                          <DollarSign className="h-3 w-3" />
                          <span>{hand.pot_size}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-slate-300 border-slate-600"
                        onClick={() => setSelectedHand(hand)}
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        Ver Análise
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-4xl max-h-[80vh] bg-slate-800 border-slate-700">
                      <DialogHeader>
                        <DialogTitle className="text-white">
                          Análise da Mão #{selectedHand?.hand_id}
                        </DialogTitle>
                        <DialogDescription className="text-slate-400">
                          {selectedHand?.hero_name} - {selectedHand?.hero_cards} - {selectedHand?.hero_position}
                        </DialogDescription>
                      </DialogHeader>
                      <ScrollArea className="h-96 w-full">
                        <div className="space-y-4 p-4">
                          {/* Informações da Mão */}
                          <div className="bg-slate-700/50 p-4 rounded-lg">
                            <h4 className="font-medium text-white mb-2">Informações da Mão</h4>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="text-slate-400">Herói:</span>
                                <span className="text-white ml-2">{selectedHand?.hero_name}</span>
                              </div>
                              <div>
                                <span className="text-slate-400">Cartas:</span>
                                <span className="text-white ml-2">{selectedHand?.hero_cards}</span>
                              </div>
                              <div>
                                <span className="text-slate-400">Posição:</span>
                                <span className="text-white ml-2">{selectedHand?.hero_position}</span>
                              </div>
                              <div>
                                <span className="text-slate-400">Ação:</span>
                                <span className="text-white ml-2">{selectedHand?.hero_action}</span>
                              </div>
                              {selectedHand?.board_cards && (
                                <div>
                                  <span className="text-slate-400">Board:</span>
                                  <span className="text-white ml-2">{selectedHand?.board_cards}</span>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Análise da IA */}
                          <div className="bg-slate-700/50 p-4 rounded-lg">
                            <h4 className="font-medium text-white mb-2">Análise da IA</h4>
                            <div className="text-slate-300 whitespace-pre-wrap">
                              {selectedHand?.ai_analysis || 'Análise não disponível'}
                            </div>
                          </div>

                          {/* Hand History Completa */}
                          <div className="bg-slate-700/50 p-4 rounded-lg">
                            <h4 className="font-medium text-white mb-2">Hand History Completa</h4>
                            <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono bg-slate-800 p-3 rounded overflow-x-auto">
                              {selectedHand?.raw_hand}
                            </pre>
                          </div>
                        </div>
                      </ScrollArea>
                    </DialogContent>
                  </Dialog>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDeleteHand(hand.id)}
                    className="text-red-400 border-red-600 hover:bg-red-600/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Preview da análise */}
              {hand.ai_analysis && (
                <div className="mt-3 p-3 bg-slate-700/30 rounded text-sm text-slate-300">
                  <div className="line-clamp-2">
                    {hand.ai_analysis.substring(0, 150)}...
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

