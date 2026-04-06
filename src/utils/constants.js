export const POLICY_DEFAULTS = {
  tax_rate: 25,
  fuel_price: 3.5,
  subsidy: 15,
  public_spending: 30,
  interest_rate: 5,
  environmental_regulation: 50,
}

export const POLICY_CONFIG = {
  tax_rate: {
    label: 'Tax Rate',
    unit: '%',
    min: 0,
    max: 60,
    step: 0.5,
    description: 'Corporate and income tax rate',
    icon: 'Receipt',
    color: '#06b6d4',
  },
  fuel_price: {
    label: 'Fuel Price',
    unit: '$/gal',
    min: 1,
    max: 10,
    step: 0.1,
    description: 'Average gasoline price per gallon',
    icon: 'Fuel',
    color: '#f59e0b',
  },
  subsidy: {
    label: 'Subsidy Level',
    unit: '%',
    min: 0,
    max: 50,
    step: 0.5,
    description: 'Government subsidy as % of GDP',
    icon: 'HandCoins',
    color: '#10b981',
  },
  public_spending: {
    label: 'Public Spending',
    unit: '% GDP',
    min: 10,
    max: 60,
    step: 0.5,
    description: 'Government expenditure as % of GDP',
    icon: 'Building',
    color: '#8b5cf6',
  },
  interest_rate: {
    label: 'Interest Rate',
    unit: '%',
    min: 0,
    max: 20,
    step: 0.25,
    description: 'Central bank base interest rate',
    icon: 'TrendingUp',
    color: '#ef4444',
  },
  environmental_regulation: {
    label: 'Environmental Regulation',
    unit: '/100',
    min: 0,
    max: 100,
    step: 1,
    description: 'Regulatory stringency index (0-100)',
    icon: 'Leaf',
    color: '#22c55e',
  },
}

export const OUTPUT_CONFIG = {
  gdp_growth: {
    label: 'GDP Growth',
    unit: '%',
    icon: 'TrendingUp',
    color: '#06b6d4',
    goodDirection: 'up',
  },
  inflation: {
    label: 'Inflation',
    unit: '%',
    icon: 'ArrowUpRight',
    color: '#ef4444',
    goodDirection: 'down',
  },
  employment_rate: {
    label: 'Employment Rate',
    unit: '%',
    icon: 'Users',
    color: '#10b981',
    goodDirection: 'up',
  },
  environment_score: {
    label: 'Environment Score',
    unit: '/100',
    icon: 'Leaf',
    color: '#22c55e',
    goodDirection: 'up',
  },
  public_satisfaction: {
    label: 'Public Satisfaction',
    unit: '%',
    icon: 'Heart',
    color: '#f59e0b',
    goodDirection: 'up',
  },
}

export function formatValue(value, unit) {
  if (typeof value !== 'number') return '—'
  const formatted = Math.abs(value) >= 100
    ? value.toFixed(1) : value.toFixed(2)
  return `${formatted}${unit}`
}

export function getChangeColor(value, goodDirection = 'up') {
  if (value === 0) return 'text-gray-400'
  if (goodDirection === 'up') {
    return value > 0 ? 'text-emerald-400' : 'text-red-400'
  }
  return value < 0 ? 'text-emerald-400' : 'text-red-400'
}

export function getRiskLevel(results) {
  if (!results) return { level: 'unknown', color: 'gray' }
  const { gdp_growth, inflation, employment_rate, environment_score } = results
  let risk = 0
  if (gdp_growth < 0) risk += 2
  if (gdp_growth < -2) risk += 1
  if (inflation > 8) risk += 2
  if (inflation > 12) risk += 1
  if (employment_rate < 90) risk += 2
  if (environment_score < 40) risk += 1
  
  if (risk >= 5) return { level: 'HIGH RISK', color: 'red' }
  if (risk >= 3) return { level: 'MODERATE', color: 'yellow' }
  return { level: 'STABLE', color: 'green' }
}
