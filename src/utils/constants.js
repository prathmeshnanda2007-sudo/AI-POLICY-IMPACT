export const POLICY_DEFAULTS = {
  Tax_Rate: 15.0,
  Fuel_Price: 4.5,
  Subsidy_Level: 10.0,
  Public_Spending: 30.0,
  Interest_Rate: 5.0,
  Environmental_Regulation: 50.0,
}

export const POLICY_CONFIG = {
  Tax_Rate: {
    label: 'Tax Rate',
    unit: '%',
    min: 0,
    max: 60,
    step: 0.5,
    description: 'Corporate and income tax rate',
    icon: 'Receipt',
    color: '#06b6d4',
  },
  Fuel_Price: {
    label: 'Fuel Price',
    unit: '$/gal',
    min: 1,
    max: 10,
    step: 0.1,
    description: 'Average gasoline price per gallon',
    icon: 'Zap',
    color: '#f59e0b',
  },
  Subsidy_Level: {
    label: 'Subsidy Level',
    unit: '%',
    min: 0,
    max: 50,
    step: 1,
    description: 'Government subsidy as % of GDP',
    icon: 'TrendingUp',
    color: '#10b981',
  },
  Public_Spending: {
    label: 'Public Spending',
    unit: '% GDP',
    min: 10,
    max: 60,
    step: 0.5,
    description: 'Government expenditure as % of GDP',
    icon: 'Building',
    color: '#8b5cf6',
  },
  Interest_Rate: {
    label: 'Interest Rate',
    unit: '%',
    min: 0,
    max: 20,
    step: 0.25,
    description: 'Central bank base interest rate',
    icon: 'Landmark',
    color: '#ef4444',
  },
  Environmental_Regulation: {
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
    icon: 'TrendingDown',
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
    icon: 'Smile',
    color: '#f59e0b',
    goodDirection: 'up',
  },
}

export function formatValue(value, unit) {
  if (typeof value !== 'number') return '—'
  // CO2 is very large, format with commas or K/M
  if (value > 9999) {
    if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M${unit}`
    return `${(value / 1000).toFixed(1)}k${unit}`
  }
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
  const { gdp_growth, inflation } = results
  let risk = 0
  if (gdp_growth < 0) risk += 2
  if (gdp_growth < -2) risk += 1
  if (inflation > 8) risk += 1
  if (inflation > 15) risk += 2
  
  if (risk >= 3) return { level: 'HIGH RISK', color: 'red' }
  if (risk >= 2) return { level: 'MODERATE', color: 'yellow' }
  return { level: 'STABLE', color: 'green' }
}
