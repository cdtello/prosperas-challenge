import { motion } from 'framer-motion'
import { Plus, Send } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/shared/ui/Button'
import { Card, CardHeader } from '@/shared/ui/Card'
import { Input, Select } from '@/shared/ui/Input'
import { useCreateJob } from '../model/useJobs'

const REPORT_TYPES = [
  { value: 'sales_summary', label: 'Sales Summary' },
  { value: 'revenue_by_country', label: 'Revenue by Country' },
  { value: 'user_activity', label: 'User Activity' },
  { value: 'conversion_funnel', label: 'Conversion Funnel' },
  { value: 'product_performance', label: 'Product Performance' },
]

const FORMATS = [
  { value: 'json', label: 'JSON' },
  { value: 'csv', label: 'CSV' },
  { value: 'pdf', label: 'PDF' },
]

export function CreateJobForm() {
  const { mutate, isPending } = useCreateJob()
  const [form, setForm] = useState({
    report_type: 'sales_summary',
    date_range: '',
    format: 'json',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutate(form)
    setForm(f => ({ ...f, date_range: '' }))
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-accent/15 border border-accent/25 flex items-center justify-center">
            <Plus className="w-3.5 h-3.5 text-accent-glow" />
          </div>
          <h2 className="text-sm font-semibold text-slate-200">New Report</h2>
        </div>
      </CardHeader>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Select
          label="Report Type"
          value={form.report_type}
          onChange={e => setForm(f => ({ ...f, report_type: e.target.value }))}
        >
          {REPORT_TYPES.map(t => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </Select>

        <Input
          label="Date Range"
          placeholder="e.g. 2024-01-01 / 2024-12-31"
          value={form.date_range}
          onChange={e => setForm(f => ({ ...f, date_range: e.target.value }))}
          required
        />

        <Select
          label="Format"
          value={form.format}
          onChange={e => setForm(f => ({ ...f, format: e.target.value }))}
        >
          {FORMATS.map(f => (
            <option key={f.value} value={f.value}>{f.label}</option>
          ))}
        </Select>

        <motion.div whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}>
          <Button type="submit" loading={isPending} className="w-full mt-2 glow-accent" size="md">
            <Send className="w-4 h-4" />
            Generate Report
          </Button>
        </motion.div>
      </form>
    </Card>
  )
}
