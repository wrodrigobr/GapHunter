import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LogOut, Upload, History, User, TrendingUp, Users, Eye, CreditCard } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { userService } from '../lib/api';
import UploadSection from './UploadSection';
import HandsHistory from './HandsHistory';
import PerformanceTracker from './PerformanceTracker';
import CoachingModule from './CoachingModule';
import GapHunterVision from './GapHunterVision';
import SubscriptionClub from './SubscriptionClub';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const statsData = await userService.getStats();
        setStats(statsData);
      } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, []);

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">GapHunter</h1>
            <span className="text-slate-400">|</span>
            <span className="text-slate-300">Bem-vindo, {user?.username}</span>
          </div>
          <Button variant="outline" onClick={handleLogout} className="text-slate-300 border-slate-600">
            <LogOut className="w-4 h-4 mr-2" />
            Sair
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Total de Mãos</CardTitle>
              <History className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {loading ? '...' : stats?.total_hands || 0}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Membro desde</CardTitle>
              <User className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {loading ? '...' : stats?.member_since ? new Date(stats.member_since).toLocaleDateString('pt-BR') : 'N/A'}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Status</CardTitle>
              <div className="h-2 w-2 bg-green-500 rounded-full"></div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">Ativo</div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="upload" className="w-full">
          <TabsList className="grid w-full grid-cols-6 bg-slate-800/50 border-slate-700">
            <TabsTrigger value="upload" className="data-[state=active]:bg-slate-700">
              <Upload className="w-4 h-4 mr-2" />
              Upload de Mãos
            </TabsTrigger>
            <TabsTrigger value="history" className="data-[state=active]:bg-slate-700">
              <History className="w-4 h-4 mr-2" />
              Histórico
            </TabsTrigger>
            <TabsTrigger value="performance" className="data-[state=active]:bg-slate-700">
              <TrendingUp className="w-4 h-4 mr-2" />
              Performance
            </TabsTrigger>
            <TabsTrigger value="coaching" className="data-[state=active]:bg-slate-700">
              <Users className="w-4 h-4 mr-2" />
              Coaching
            </TabsTrigger>
            <TabsTrigger value="vision" className="data-[state=active]:bg-slate-700">
              <Eye className="w-4 h-4 mr-2" />
              Vision
            </TabsTrigger>
            <TabsTrigger value="subscription" className="data-[state=active]:bg-slate-700">
              <CreditCard className="w-4 h-4 mr-2" />
              Assinatura & Club
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="mt-6">
            <UploadSection onUploadSuccess={() => setStats(prev => ({ ...prev, total_hands: (prev?.total_hands || 0) + 1 }))} />
          </TabsContent>

          <TabsContent value="history" className="mt-6">
            <HandsHistory />
          </TabsContent>

          <TabsContent value="performance" className="mt-6">
            <PerformanceTracker />
          </TabsContent>

          <TabsContent value="coaching" className="mt-6">
            <CoachingModule />
          </TabsContent>

          <TabsContent value="vision" className="mt-6">
            <GapHunterVision />
          </TabsContent>

          <TabsContent value="subscription" className="mt-6">
            <SubscriptionClub />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

