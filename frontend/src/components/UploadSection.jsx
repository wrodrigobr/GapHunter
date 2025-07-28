import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { handsService } from '../lib/api';

export default function UploadSection({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef();

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.txt')) {
        setError('Apenas arquivos .txt são aceitos');
        return;
      }
      setFile(selectedFile);
      setError('');
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);
    setError('');
    setResult(null);

    try {
      // Simular progresso
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await handsService.uploadFile(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setResult(response);
      
      if (onUploadSuccess) {
        onUploadSuccess();
      }
      
      // Reset form
      setTimeout(() => {
        setFile(null);
        setUploadProgress(0);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }, 2000);
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Erro ao fazer upload do arquivo');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith('.txt')) {
      setFile(droppedFile);
      setError('');
      setResult(null);
    } else {
      setError('Apenas arquivos .txt são aceitos');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div className="space-y-6">
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Upload de Hand History</CardTitle>
          <CardDescription className="text-slate-400">
            Faça upload do arquivo .txt com suas mãos do PokerStars para análise
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                {result.message} - {result.hands_processed} mãos processadas
              </AlertDescription>
            </Alert>
          )}

          {/* Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center hover:border-slate-500 transition-colors"
          >
            <Upload className="mx-auto h-12 w-12 text-slate-400 mb-4" />
            <div className="space-y-2">
              <p className="text-slate-300">
                Arraste e solte seu arquivo .txt aqui ou
              </p>
              <Button
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                className="text-slate-300 border-slate-600"
              >
                Selecionar arquivo
              </Button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Selected File */}
          {file && (
            <div className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg">
              <FileText className="h-5 w-5 text-slate-400" />
              <div className="flex-1">
                <p className="text-sm font-medium text-white">{file.name}</p>
                <p className="text-xs text-slate-400">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <Button
                onClick={handleUpload}
                disabled={uploading}
                className="bg-primary hover:bg-primary/90"
              >
                {uploading ? 'Processando...' : 'Analisar'}
              </Button>
            </div>
          )}

          {/* Progress Bar */}
          {uploading && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Processando arquivo...</span>
                <span className="text-slate-400">{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} className="w-full" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Instructions */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg">Como obter o arquivo de mãos?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-slate-300">
          <div className="space-y-2">
            <h4 className="font-medium">No PokerStars:</h4>
            <ol className="list-decimal list-inside space-y-1 text-sm">
              <li>Vá em "Opções" → "Histórico de Mãos"</li>
              <li>Selecione o período desejado</li>
              <li>Clique em "Solicitar Mãos"</li>
              <li>Baixe o arquivo .txt quando estiver pronto</li>
            </ol>
          </div>
          <div className="text-sm text-slate-400 bg-slate-700/30 p-3 rounded">
            <strong>Dica:</strong> O arquivo pode conter múltiplas mãos. Nossa IA analisará cada uma individualmente.
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

