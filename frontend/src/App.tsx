import { FormEvent, useEffect, useState } from 'react';
import {
  Badge,
  Button,
  Card,
  Divider,
  Spinner,
  Text,
  Textarea,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { api, type AnalysisHistoryRow, type AnalysisResult, type ApiHealth, type ExtractedProfile } from './api';

const useStyles = makeStyles({
  shell: {
    background: tokens.colorNeutralBackground2,
    minHeight: '100vh',
    color: tokens.colorNeutralForeground1,
    fontFamily: 'Inter, Segoe UI, sans-serif',
  },
  topBar: {
    background: tokens.colorNeutralBackground1,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 2rem',
    gap: '1rem',
  },
  nav: { display: 'flex', gap: '1.25rem', alignItems: 'center' },
  page: { maxWidth: '1120px', margin: '0 auto', padding: '2rem' },
  layout: { display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(280px, 0.75fr)', gap: '1.25rem' },
  card: {
    background: tokens.colorNeutralBackground1,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderRadius: '12px',
    boxShadow: '0 6px 16px rgba(15, 23, 42, 0.05)',
    padding: '1.25rem',
  },
  stack: { display: 'grid', gap: '1rem' },
  label: { display: 'block', marginBottom: '0.4rem' },
  field: { width: '100%' },
  table: { width: '100%', borderCollapse: 'collapse', marginTop: '1rem' },
  cell: {
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    padding: '0.75rem 0.5rem',
    textAlign: 'left',
    verticalAlign: 'top',
  },
  tags: { display: 'flex', flexWrap: 'wrap', gap: '0.5rem', margin: '0.75rem 0' },
  muted: { color: tokens.colorNeutralForeground3 },
  error: { color: tokens.colorPaletteRedForeground1 },
  score: { color: '#2563eb', fontSize: '2.75rem', fontWeight: 700, lineHeight: 1.1 },
  status: { display: 'flex', gap: '0.5rem', alignItems: 'center' },
});

function getStatus(score: number): string {
  if (score >= 80) return 'Strong match';
  if (score >= 60) return 'Good match';
  return 'Needs review';
}

function App() {
  const styles = useStyles();
  const [resumeText, setResumeText] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [profile, setProfile] = useState<ExtractedProfile | null>(null);
  const [history, setHistory] = useState<AnalysisHistoryRow[]>([]);
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    Promise.all([api.getHealth(), api.listAnalyses()])
      .then(([healthResult, analysisRows]) => {
        if (!mounted) return;
        setHealth(healthResult);
        setHistory(analysisRows);
      })
      .catch((reason: unknown) => {
        if (mounted) setError(reason instanceof Error ? reason.message : 'Unable to connect to the API.');
      });
    return () => {
      mounted = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const uploaded = resumeFile
        ? await api.uploadResumeFile(resumeFile, jobDescription.trim())
        : await api.uploadResume({ file: resumeText.trim(), jobDescription: jobDescription.trim() });
      const computed = await api.analyzeResume(uploaded.resumeId, uploaded.jobId);
      const persisted = await api.getAnalysis(computed.id);
      const [rows, resume] = await Promise.all([api.listAnalyses(), api.getResume(uploaded.resumeId)]);
      setAnalysis(persisted);
      setHistory(rows);
      setProfile(resume.profile);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.shell}>
      <header className={`${styles.topBar} app-top-bar`}>
        <Text weight="semibold" size={500}>Resume Analyzer</Text>
        <nav className={`${styles.nav} app-nav`} aria-label="Main navigation">
          <Text>Screen candidates</Text>
          <Text>Analysis history</Text>
        </nav>
        <div className={styles.status}>
          <Badge color={health?.status === 'ok' ? 'success' : 'warning'} appearance="tint">
            API {health?.status ?? 'connecting'}
          </Badge>
        </div>
      </header>

      <main className={`${styles.page} app-page`}>
        <div className={`${styles.layout} app-layout`}>
          <Card className={styles.card}>
            <div className={styles.stack}>
              <div>
                <Text size={800} weight="semibold">Candidate fit analysis</Text>
                <Text as="p" className={styles.muted}>Compare resume text with a role description. Results are saved by the API.</Text>
              </div>
              <Divider />
              <form className={styles.stack} onSubmit={handleSubmit}>
                <label>
                  <Text weight="semibold" className={styles.label}>Resume document (optional)</Text>
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                    onChange={(event) => setResumeFile(event.currentTarget.files?.[0] ?? null)}
                  />
                  <Text as="p" className={styles.muted}>PDF, DOCX, TXT, PNG, or JPG; up to 10 MB. Image OCR requires Tesseract installed on the API host.</Text>
                </label>
                <label>
                  <Text weight="semibold" className={styles.label}>Resume text</Text>
                  <Textarea
                    className={styles.field}
                    value={resumeText}
                    onChange={(_event, data) => setResumeText(data.value)}
                    placeholder={resumeFile ? 'A selected document will be analyzed instead' : "Paste the candidate's resume text"}
                    resize="vertical"
                    rows={8}
                    required={!resumeFile}
                  />
                </label>
                <label>
                  <Text weight="semibold" className={styles.label}>Job description</Text>
                  <Textarea
                    className={styles.field}
                    value={jobDescription}
                    onChange={(_event, data) => setJobDescription(data.value)}
                    placeholder="Paste the role description and required skills"
                    resize="vertical"
                    rows={7}
                    required
                  />
                </label>
                {error && <Text role="alert" className={styles.error}>{error}</Text>}
                <Button appearance="primary" type="submit" disabled={loading || !health}>
                  {loading ? <Spinner size="tiny" label="Analyzing resume" /> : 'Analyze candidate'}
                </Button>
              </form>
            </div>
          </Card>

          <Card className={styles.card}>
            <Text size={700} weight="semibold">Analysis result</Text>
            {!analysis ? (
              <Text as="p" className={styles.muted}>
                Submit a resume and role description to see the live analysis here.
              </Text>
            ) : (
              <div className={styles.stack} style={{ marginTop: '1rem' }}>
                <div className={styles.score}>{analysis.score}<Text size={400} className={styles.muted}> / 100</Text></div>
                <Badge appearance="tint" color={analysis.score >= 80 ? 'success' : analysis.score >= 60 ? 'informative' : 'warning'}>
                  {getStatus(analysis.score)}
                </Badge>
                <Text>{analysis.summary}</Text>
                <Text size={300} className={styles.muted}>Skill fit 40% · Experience indicator 30% · Education indicator 20% · Text overlap 10%. Text overlap is not an embedding model.</Text>
                <div className={styles.stack}>
                  <Text>Skill coverage: {analysis.skillScore}%</Text>
                  <Text>Experience indicator: {analysis.experienceScore}%</Text>
                  <Text>Education indicator: {analysis.educationScore}%</Text>
                  <Text>Text overlap: {analysis.semanticScore}%</Text>
                </div>
                <Divider />
                <div>
                  <Text weight="semibold">Matched skills</Text>
                  <div className={styles.tags}>
                    {analysis.matchedSkills.length ? analysis.matchedSkills.map((skill) => (
                      <Badge key={skill} appearance="tint" color="success">{skill}</Badge>
                    )) : <Text className={styles.muted}>No matching skills detected.</Text>}
                  </div>
                </div>
                {analysis.recommendations.map((recommendation) => (
                  <Text key={recommendation} className={styles.muted}>{recommendation}</Text>
                ))}
                {profile && (
                  <>
                    <Divider />
                    <Text weight="semibold">Extracted profile signals (personal identifiers hidden)</Text>
                    <Text>Skills: {profile.skills.length ? profile.skills.join(', ') : 'None detected'}</Text>
                    <Text>Education entries detected: {profile.educationEntries}</Text>
                    <Text>Experience entries detected: {profile.experienceEntries}</Text>
                  </>
                )}
                <div>
                  <Text weight="semibold">Skills to review</Text>
                  <div className={styles.tags}>
                    {analysis.missingSkills.length ? analysis.missingSkills.map((skill) => (
                      <Badge key={skill} appearance="tint" color="warning">{skill}</Badge>
                    )) : <Text className={styles.muted}>No missing skills detected.</Text>}
                  </div>
                </div>
              </div>
            )}
          </Card>
        </div>

        <Card className={styles.card} style={{ marginTop: '1.25rem' }}>
          <Text size={700} weight="semibold">Saved analyses</Text>
          {history.length === 0 ? (
            <Text as="p" className={styles.muted}>No analyses have been saved yet.</Text>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th className={styles.cell}>Candidate</th>
                  <th className={styles.cell}>Role</th>
                  <th className={styles.cell}>Score</th>
                  <th className={styles.cell}>Status</th>
                </tr>
              </thead>
              <tbody>
                {history.map((row) => (
                  <tr key={row.id}>
                    <td className={styles.cell}>{row.candidate}</td>
                    <td className={styles.cell}>{row.jobTitle}</td>
                    <td className={styles.cell}>{row.score}</td>
                    <td className={styles.cell}>{getStatus(row.score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>
      </main>
    </div>
  );
}

export default App;
